"""Stage: assembly. Narration timed to shots, music ducked under voice, bilingual opening
title, subtitles, and AI end card with smooth ASS fades, loudness normalization, and 9:16 + 16:9 exports.
`python -m pipeline.assemble radio` builds the subtitled radio cut."""
import subprocess, sys, textwrap, time
from pipeline.common import *
from pipeline.shots import ASPECTS

FONT = "Ebrima"  # Includes crisp Ethiopic (Ge'ez) and Latin glyphs on Windows


def media_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0.0


def ff_path(p):
    """Escape a path for FFmpeg filter options (handles Windows drive colons and spaces)."""
    return "'" + p.resolve().as_posix().replace("\\", "/").replace(":", r"\:") + "'"


def ass_time(t):
    t = max(0.0, t)
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{int(s):02d}.{int((s % 1) * 100):02d}"


def write_ass(path, W, H, title_cue, sub_cues, end_cue, sizes):
    """Write a styled ASS file with smooth fade-in/out on title, subtitles, and end card."""
    ts, fs, es, tmv, mv = sizes
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,{FONT},{ts},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,1,0,0,0,100,100,0,0,1,3,1,8,40,40,{tmv},1
Style: Sub,{FONT},{fs},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2.5,1,2,40,40,{mv},1
Style: EndCard,{FONT},{es},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,0,5,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [hdr]
    def esc(txt): return txt.replace("\n", r"\N")
    if title_cue:
        a, b, txt = title_cue
        lines.append(f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Title,,0,0,0,,{{\\fad(700,700)}}{esc(txt)}\n")
    for a, b, txt in sub_cues:
        lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,{{\\fad(150,150)}}{esc(txt)}\n")
    if end_cue:
        a, b, txt = end_cue
        lines.append(f"Dialogue: 2,{ass_time(a)},{ass_time(b)},EndCard,,0,0,0,,{{\\fad(600,600)}}{esc(txt)}\n")
    path.write_text("".join(lines), encoding="utf-8")


def build_bilingual_cues(sb, durs, width):
    """Build (start, end, active language + English) subtitle cues timed to each shot."""
    cues, t = [], 0.0
    lang = LANG()
    for s, d in zip(sb["shots"], durs):
        pri = "\n".join(textwrap.wrap(s["narration"].get(lang, "").strip(), width))
        en = "\n".join(textwrap.wrap(s["narration"]["en"].strip(), width))
        txt = f"{pri}\n{en}" if (pri and lang != "en") else en
        cues.append((t + 0.15, t + d - 0.15, txt))
        t += d
    return cues


def title_text(sb):
    am = sb.get("title_am", "").strip()
    return f"{sb['title']}\n{am}" if am else sb["title"]


def narration_track(sb, work):
    parts = []
    for s in sb["shots"]:
        d = shot_seconds(s); p = work / f"n_{s['id']}.wav"
        aud = narration_audio_path(s["id"])
        tempo = narration_tempo(s["id"])
        if aud.exists():
            af = f"atempo={tempo},apad=whole_dur={d}" if abs(tempo - 1.0) > 1e-3 else f"apad=whole_dur={d}"
            ff(["-i", str(aud), "-af", af, "-ar", "48000", "-ac", "1", str(p)])
        else:
            ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(d), str(p)])
        parts.append(p)
    lst = work / "nar.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    out = work / "narration_all.wav"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def music_track(total, work):
    chosen = OUT / "music" / "chosen.wav"; out = work / "music_total.wav"
    fade = f"afade=t=in:st=0:d=1.2,afade=t=out:st={max(total-3,0)}:d=3"
    if chosen.exists():
        ff(["-stream_loop", "-1", "-i", str(chosen), "-t", str(total), "-af", f"{fade},aresample=48000", "-ac", "2", str(out)])
        return out, "chosen"
    ff(["-f", "lavfi", "-i", "sine=f=196:d=%s" % total, "-f", "lavfi", "-i", "sine=f=294:d=%s" % total,
        "-filter_complex", f"[0][1]amix=inputs=2,lowpass=f=650,volume=0.14,{fade}", "-ar", "48000", "-ac", "2", str(out)])
    return out, "placeholder"


def mix(nar, music, total, out):
    fade_out = f"afade=t=in:st=0:d=0.6,afade=t=out:st={max(total-1.4,0):.2f}:d=1.4"
    fc = (f"[1:a]aformat=channel_layouts=stereo[m];[0:a]aformat=channel_layouts=stereo,asplit[n1][n2];"
          f"[m][n1]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[duck];"
          f"[duck][n2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11,{fade_out}[a]")
    ff(["-i", str(nar), "-i", str(music), "-filter_complex", fc, "-map", "[a]", "-t", str(total), "-ar", "48000", str(out)])


def make_mobile_copies():
    """Export 720p (~11-12 MB) WhatsApp/Telegram-friendly copies from existing 9:16 final films."""
    lang = LANG()
    suffix = "" if lang == "am" else f"_{lang}"
    src = OUT / "final" / f"film_9x16{suffix}.mp4"
    if not src.exists():
        raise SystemExit(f"missing {src.name} (run assemble film first)")
    dst = OUT / "final" / f"film_9x16{suffix}_mobile.mp4"
    crf = os.environ.get("MOBILE_CRF", "24")
    t0 = time.time()
    ff(["-i", str(src), "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", crf, "-preset", "slow",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)])
    dur = media_duration(dst)
    log_run("assemble", "ffmpeg-mobile", None, {"lang": lang, "crf": crf, "mb": round(dst.stat().st_size / 1048576, 2), "seconds": round(dur, 2)}, None, time.time() - t0)
    print(f"{dst.name}: {dur:.2f}s ({dst.stat().st_size / 1048576:.2f} MB)")


def main(mode="film"):
    if mode == "mobile":
        make_mobile_copies(); return
    sb = load_storyboard(); work = OUT / "work"; work.mkdir(parents=True, exist_ok=True)
    (OUT / "final").mkdir(parents=True, exist_ok=True); t0 = time.time()
    durs = [shot_seconds(s) for s in sb["shots"]]; body = sum(durs)
    end = 0 if mode == "radio" else sb["end_card"]["seconds"]; total = body + end
    nar = narration_track(sb, work); nar_ext = work / "narration_ext.wav"
    ff(["-i", str(nar), "-af", f"apad=whole_dur={total}", str(nar_ext)])
    music, kind = music_track(total, work); audio = work / "mix.wav"; mix(nar_ext, music, total, audio)
    title_cue = (0.35, min(4.6, body - 0.2), title_text(sb))
    if mode == "radio":
        ass_p = work / f"radio_{LANG()}.ass"
        write_ass(ass_p, 640, 360, title_cue, build_bilingual_cues(sb, durs, 42), None, (26, 20, 22, 24, 24))
        vf = f"fade=t=in:st=0:d=0.8,fade=t=out:st={max(total-1.0,0):.2f}:d=1.0,ass={ff_path(ass_p)}"
        ff(["-f", "lavfi", "-i", f"color=c=0x101010:s=640x360:r=24:d={total}", "-i", str(audio),
            "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            str(OUT / "final" / f"radio_cut_{LANG()}.mp4")])
        log_run("assemble", "ffmpeg", None, {"mode": "radio", "lang": LANG(), "music": kind, "seconds": total}, None, time.time() - t0)
        print(f"radio cut: {total:.1f}s (music: {kind})"); return
    fade_d = 0.65
    shots_dir = OUT / "shots" / LANG()
    for asp, (W, H) in ASPECTS.items():
        clips = [shots_dir / f"shot_{s['id']}_{asp}.mp4" for s in sb["shots"]]
        missing = [c.name for c in clips if not c.exists()]
        if missing: raise SystemExit(f"missing shot clips in {shots_dir} (run keyframes + shots first): {missing[:3]}...")
        ass_p = work / f"overlay_{asp}_{LANG()}.ass"
        wrap_w = 32 if asp == "9x16" else 44
        end_w = 28 if asp == "9x16" else 44
        end_txt = "\n".join("\n".join(textwrap.wrap(ln, end_w)) for ln in sb["end_card"]["text"].splitlines())
        sizes = (68, 46, 48, 150, 210) if asp == "9x16" else (56, 38, 44, 48, 48)
        write_ass(ass_p, W, H, title_cue, build_bilingual_cues(sb, durs, wrap_w), (body + 0.15, total - 0.15, end_txt), sizes)
        endclip = work / f"end_{asp}.mp4"
        ff(["-f", "lavfi", "-i", f"color=c=0x0a0a0a:s={W}x{H}:r=24:d={end}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(endclip)])
        # Ensure every pre-xfade clip spans at least cd + fade_d via clone padding + trim so xfade never aborts early.
        all_clips = clips + [endclip]
        clip_durs = durs + [end]
        inputs = []
        for c in all_clips:
            inputs += ["-i", str(c)]
        fc_parts = []
        for idx, cd in enumerate(clip_durs):
            target_len = cd + fade_d if idx < len(all_clips) - 1 else cd
            fc_parts.append(
                f"[{idx}:v]setpts=PTS-STARTPTS,fps=24,format=yuv420p,"
                f"tpad=stop_mode=clone:stop_duration={fade_d + 5:.2f},trim=duration={target_len:.3f},setpts=PTS-STARTPTS[v{idx}]"
            )
        cur = "v0"
        offset = 0.0
        for idx in range(len(all_clips) - 1):
            offset += clip_durs[idx]
            nxt = f"v{idx+1}"
            out_lbl = f"xf{idx}"
            # Smooth fadeblack dip before shot 07 breakthrough and into the closing end card; xfade dissolves elsewhere.
            trans = "fadeblack" if idx in (5, len(clips) - 1) else "fade"
            fc_parts.append(f"[{cur}][{nxt}]xfade=transition={trans}:duration={fade_d}:offset={offset:.3f}[{out_lbl}]")
            cur = out_lbl
        fc_parts.append(
            f"[{cur}]fade=t=in:st=0:d=1.2,ass={ff_path(ass_p)},fade=t=out:st={max(total-1.0,0):.2f}:d=1.0[vout]"
        )
        suffix = "" if LANG() == "am" else f"_{LANG()}"
        out = OUT / "final" / f"film_{asp}{suffix}.mp4"
        a_idx = len(all_clips)
        crf = os.environ.get("VIDEO_CRF", "24")
        ff(inputs + ["-i", str(audio), "-filter_complex", ";".join(fc_parts),
                     "-map", "[vout]", "-map", f"{a_idx}:a",
                     "-c:v", "libx264", "-crf", crf, "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "24",
                     "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", str(out)])
        actual = media_duration(out)
        if abs(actual - total) > 0.6:
            raise RuntimeError(f"{out.name} duration mismatch: expected {total:.2f}s, got {actual:.2f}s")
        print(f"{out.name}: {actual:.2f}s (expected {total:.2f}s, music: {kind})")
    log_run("assemble", "ffmpeg", None, {"mode": "film", "lang": LANG(), "music": kind, "seconds": total}, None, time.time() - t0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "film")
