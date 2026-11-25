"""Stage: assembly. Narration track timed to shots, music ducked under voice, subtitles, loudness, end card, 2 aspects.
`python -m pipeline.assemble radio` builds the radio cut (narration + placeholder music on black)."""
import sys, textwrap, time
from pipeline.common import *
from pipeline.shots import ASPECTS

def srt_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n")

def narration_track(sb, work):
    parts, t = [], 0.0
    for s in sb["shots"]:
        d = shot_seconds(s); p = work / f"n_{s['id']}.wav"
        wav = OUT / "narration" / LANG() / f"shot_{s['id']}.wav"
        if wav.exists():
            ff(["-i", str(wav), "-af", f"apad=whole_dur={d}", "-ar", "48000", "-ac", "1", str(p)])
        else:
            ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(d), str(p)])
        parts.append(p)
    lst = work / "nar.txt"; lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    out = work / "narration_all.wav"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out

def music_track(total, work):
    chosen = OUT / "music" / "chosen.wav"; out = work / "music_total.wav"
    fade = f"afade=t=out:st={max(total-3,0)}:d=3"
    if chosen.exists():
        ff(["-stream_loop", "-1", "-i", str(chosen), "-t", str(total), "-af", f"{fade},aresample=48000", "-ac", "2", str(out)])
        return out, "chosen"
    ff(["-f", "lavfi", "-i", "sine=f=196:d=%s" % total, "-f", "lavfi", "-i", "sine=f=294:d=%s" % total,
        "-filter_complex", f"[0][1]amix=inputs=2,volume=0.25,{fade}", "-ar", "48000", "-ac", "2", str(out)])
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
    if mode == "radio":
        ff(["-f", "lavfi", "-i", f"color=c=black:s=640x360:r=24:d={total}", "-i", str(audio), "-c:v", "libx264", "-c:a", "aac", "-shortest", str(OUT / "final" / f"radio_cut_{LANG()}.mp4")])
        log_run("assemble", "ffmpeg", None, {"mode": "radio", "music": kind, "seconds": total}, None, time.time() - t0)
        print(f"radio cut: {total:.1f}s (music: {kind})"); return
    cues, t = [], 0.0
    for s, d in zip(sb["shots"], durs):
        cues.append((t + 0.2, t + d - 0.2, "\n".join(textwrap.wrap(s["narration"]["en"], 40)))); t += d
    write_srt(work / "subs.srt", cues); write_srt(work / "end.srt", [(body + 0.3, total - 0.2, sb["end_card"]["text"])])
    for asp, (W, H) in ASPECTS.items():
        clips = [OUT / "shots" / f"shot_{s['id']}_{asp}.mp4" for s in sb["shots"]]
        missing = [c.name for c in clips if not c.exists()]
        if missing: raise SystemExit(f"missing shot clips (run keyframes + shots first): {missing[:3]}...")
        endclip = work / f"end_{asp}.mp4"
        ff(["-f", "lavfi", "-i", f"color=c=0x101010:s={W}x{H}:r=24:d={end}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(endclip)])
        lst = work / f"v_{asp}.txt"; lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips + [endclip]))
        # libass sizes fonts on a 288px-high virtual canvas, not real pixels
        fs, es = (9, 14) if asp == "9x16" else (13, 18); mv = 38 if asp == "9x16" else 18
        vf = (f"subtitles={work/'subs.srt'}:force_style='Fontsize={fs},Outline=2,MarginV={mv}',"
              f"subtitles={work/'end.srt'}:force_style='Alignment=10,Fontsize={es}'")
        out = OUT / "final" / f"film_{asp}.mp4"
        ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(audio), "-vf", vf, "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)])
        print(f"{out.name}: {total:.1f}s (music: {kind})")
    log_run("assemble", "ffmpeg", None, {"mode": "film", "music": kind, "seconds": total}, None, time.time() - t0)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "film")
