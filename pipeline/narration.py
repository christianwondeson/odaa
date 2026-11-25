"""Stage: narration. One WAV per shot per language via Gemini TTS. Cached by text+voice+style+model."""
import time
from pipeline.common import *
from pipeline.providers import gemini_tts

def main(only=None):
    load_env(); sb = load_storyboard()
    model = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    n = sb["narration"]; lang = LANG()
    (OUT / "narration" / lang).mkdir(parents=True, exist_ok=True)
    for s in sb["shots"]:
        if only and s["id"] != only: continue
        out = OUT / "narration" / lang / f"shot_{s['id']}.wav"
        text = s["narration"][lang].strip()
        d = digest(text, n["voice"], n["style_instruction"], lang, model)
        if is_fresh(f"narration:{lang}:{s['id']}", d, out):
            print(f"shot {s['id']}: cached"); continue
        t = time.time()
        try:
            wav = retry(lambda: gemini_tts(text, n["style_instruction"], n["voice"], model))
        except Exception as e:
            log_run("narration", model, s["id"], {"lang": lang, "chars": len(text)}, None, time.time() - t, 0, "error", str(e)[:200]); raise
        out.write_bytes(wav)
        log_run("narration", model, s["id"], {"voice": n["voice"], "lang": lang, "chars": len(text)}, None, time.time() - t)
        mark(f"narration:{lang}:{s['id']}", d); print(f"shot {s['id']}: generated")

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
