"""Stage: assembly. Narration timed to shots, music ducked under voice, bilingual Amharic+English
title and subtitles, loudness normalization, bilingual AI end card, and 9:16 + 16:9 exports.
`python -m pipeline.assemble radio` builds the subtitled radio cut."""
import sys, textwrap, time
from pipeline.common import *
from pipeline.shots import ASPECTS

FONT = "Ebrima"  # Includes crisp Ethiopic (Ge'ez) and Latin glyphs on Windows

def ff_path(p):
    """Escape a path for FFmpeg filter options (handles Windows drive colons and spaces)."""
    return "'" + p.resolve().as_posix().replace("\\", "/").replace(":", r"\:") + "'"

def srt_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n")

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
    fc = ("[1:a]aformat=channel_layouts=stereo[m];[0:a]aformat=channel_layouts=stereo,asplit[n1][n2];"
          "[m][n1]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[duck];"
          "[duck][n2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11[a]")
    ff(["-i", str(nar), "-i", str(music), "-filter_complex", fc, "-map", "[a]", "-t", str(total), "-ar", "48000", str(out)])

def main(mode="film"):
    sb = load_storyboard(); work = OUT / "work"; work.mkdir(parents=True, exist_ok=True)
    (OUT / "final").mkdir(parents=True, exist_ok=True); t0 = time.time()
    durs = [shot_seconds(s) for s in sb["shots"]]; body = sum(durs)
    end = 0 if mode == "radio" else sb["end_card"]["seconds"]; total = body + end
    nar = narration_track(sb, work); nar_ext = work / "narration_ext.wav"
    ff(["-i", str(nar), "-af", f"apad=whole_dur={total}", str(nar_ext)])
    music, kind = music_track(total, work); audio = work / "mix.wav"; mix(nar_ext, music, total, audio)
    write_srt(work / "title.srt", [(0.15, min(4.5, body - 0.2), title_text(sb))])
    if mode == "radio":
        write_srt(work / "subs_radio.srt", build_bilingual_cues(sb, durs, 42))
        vf = (f"subtitles={ff_path(work/'title.srt')}:force_style='FontName={FONT},Alignment=6,Fontsize=14,Outline=2,MarginV=16',"
              f"subtitles={ff_path(work/'subs_radio.srt')}:force_style='FontName={FONT},Alignment=2,Fontsize=11,Outline=2,MarginV=14'")
        ff(["-f", "lavfi", "-i", f"color=c=0x101010:s=640x360:r=24:d={total}", "-i", str(audio),
            "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            str(OUT / "final" / f"radio_cut_{LANG()}.mp4")])
        log_run("assemble", "ffmpeg", None, {"mode": "radio", "music": kind, "seconds": total}, None, time.time() - t0)
        print(f"radio cut: {total:.1f}s (music: {kind})"); return
    write_srt(work / "end.srt", [(body + 0.3, total - 0.2, sb["end_card"]["text"])])
    fade_d = 0.65
    for asp, (W, H) in ASPECTS.items():
        clips = [OUT / "shots" / f"shot_{s['id']}_{asp}.mp4" for s in sb["shots"]]
        missing = [c.name for c in clips if not c.exists()]
        if missing: raise SystemExit(f"missing shot clips (run keyframes + shots first): {missing[:3]}...")
        srt_p = work / f"subs_{asp}.srt"
        write_srt(srt_p, build_bilingual_cues(sb, durs, 32 if asp == "9x16" else 44))
        endclip = work / f"end_{asp}.mp4"
        ff(["-f", "lavfi", "-i", f"color=c=0x101010:s={W}x{H}:r=24:d={end}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(endclip)])
        # Pad each clip tail by fade_d before xfade so every shot transition stays synced to narration.
        all_clips = clips + [endclip]
        clip_durs = durs + [end]
        inputs = []
        for c in all_clips:
            inputs += ["-i", str(c)]
        fc_parts = []
        for idx, cd in enumerate(clip_durs):
            pad = f",tpad=stop_mode=clone:stop_duration={fade_d}" if idx < len(all_clips) - 1 else ""
            fc_parts.append(f"[{idx}:v]setpts=PTS-STARTPTS,fps=24,format=yuv420p{pad}[v{idx}]")
        cur = "v0"
        offset = 0.0
        for idx in range(len(all_clips) - 1):
            offset += clip_durs[idx]
            nxt = f"v{idx+1}"
            out_lbl = f"xf{idx}"
            # Use dramatic dip-to-black before shot 07 breakthrough; smooth crossfades elsewhere.
            trans = "fadeblack" if idx == 5 else "fade"
            fc_parts.append(f"[{cur}][{nxt}]xfade=transition={trans}:duration={fade_d}:offset={offset:.3f}[{out_lbl}]")
            cur = out_lbl
        # libass sizes fonts on a 288px-high virtual canvas, not real pixels
        fs, ts, es = (8, 12, 11) if asp == "9x16" else (11, 16, 15)
        mv, tmv = (34, 24) if asp == "9x16" else (16, 14)
        fc_parts.append(
            f"[{cur}]fade=t=in:st=0:d=0.6,"
            f"subtitles={ff_path(work/'title.srt')}:force_style='FontName={FONT},Alignment=6,Fontsize={ts},Outline=2,MarginV={tmv}',"
            f"subtitles={ff_path(srt_p)}:force_style='FontName={FONT},Alignment=2,Fontsize={fs},Outline=2,MarginV={mv}',"
            f"subtitles={ff_path(work/'end.srt')}:force_style='FontName={FONT},Alignment=10,Fontsize={es},Outline=2'[vout]"
        )
        suffix = "" if LANG() == "am" else f"_{LANG()}"
        out = OUT / "final" / f"film_{asp}{suffix}.mp4"
        a_idx = len(all_clips)
        ff(inputs + ["-i", str(audio), "-filter_complex", ";".join(fc_parts),
                     "-map", "[vout]", "-map", f"{a_idx}:a",
                     "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24",
                     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)])
        print(f"{out.name}: {total:.1f}s (music: {kind})")
    log_run("assemble", "ffmpeg", None, {"mode": "film", "lang": LANG(), "music": kind, "seconds": total}, None, time.time() - t0)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "film")
