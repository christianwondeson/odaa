"""Stage: music. ACE-Step runs on Kaggle/Colab (see docs/kaggle_music_notes.md). This stage writes the cue sheet
(spotting notes with timecodes) from the storyboard and checks the chosen score exists."""
import json
from pipeline.common import *

def main():
    sb = load_storyboard(); t = 0.0; cues = []
    for s in sb["shots"]:
        d = shot_seconds(s); cues.append({"shot": s["id"], "start": round(t, 2), "end": round(t + d, 2), "cue": s["music_cue"]}); t += d
    (OUT / "music").mkdir(parents=True, exist_ok=True)
    (OUT / "music" / "cues.json").write_text(json.dumps(cues, indent=1))
    chosen = OUT / "music" / "chosen.wav"
    print(f"cue sheet written ({len(cues)} cues, {t:.1f}s)")
    print("chosen score:", "found" if chosen.exists() else "MISSING -> assemble will use a quiet placeholder pad")

if __name__ == "__main__":
    main()
