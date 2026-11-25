"""Stage: music. Writes the cue sheet (`outputs/music/cues.json`) from the storyboard,
optionally generates 3 instrumental ACE-Step 1.5 candidates via WaveSpeed when
`WAVESPEED_API_KEY` + `ENABLE_WAVESPEED=1` (or `--generate`), and checks `chosen.wav`."""
import argparse, json, os, time
from pipeline.common import *


def main(generate=False):
    load_env()
    sb = load_storyboard(); t = 0.0; cues = []
    for s in sb["shots"]:
        d = shot_seconds(s); cues.append({"shot": s["id"], "start": round(t, 2), "end": round(t + d, 2), "cue": s["music_cue"]}); t += d
    (OUT / "music").mkdir(parents=True, exist_ok=True)
    (OUT / "music" / "cues.json").write_text(json.dumps(cues, indent=1))
    chosen = OUT / "music" / "chosen.wav"
    print(f"cue sheet written ({len(cues)} cues, {t:.1f}s)")
    use_ws = generate or (bool(os.environ.get("WAVESPEED_API_KEY")) and os.environ.get("ENABLE_WAVESPEED") == "1")
    if use_ws and not chosen.exists():
        from pipeline.providers import wavespeed_acestep
        tags = "instrumental, warm acoustic strings, soft plucked krar-like lyre, sparse, gentle, emotional, 72bpm"
        for idx, seed in enumerate((101, 102, 103), 1):
            cand = OUT / "music" / f"candidate_{idx}.wav"
            if cand.exists():
                continue
            t0 = time.time()
            raw = wavespeed_acestep(tags, duration=min(int(round(t)), 90), seed=seed)
            tmp = OUT / "music" / f"candidate_{idx}.raw"
            tmp.write_bytes(raw)
            ff(["-i", str(tmp), "-ar", "48000", "-ac", "2", str(cand)])
            tmp.unlink(missing_ok=True)
            log_run("music", "wavespeed/ace-step-1.5", None, {"candidate": idx, "tags": tags}, seed, time.time() - t0, 0.027)
            print(f"generated {cand.name}")
        if (OUT / "music" / "candidate_1.wav").exists() and not chosen.exists():
            chosen.write_bytes((OUT / "music" / "candidate_1.wav").read_bytes())
    print("chosen score:", "found" if chosen.exists() else "MISSING -> assemble will use a quiet placeholder pad")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true", help="Generate 3 ACE-Step candidates via WaveSpeed")
    args = ap.parse_args()
    main(generate=args.generate)
