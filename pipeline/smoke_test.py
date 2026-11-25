"""Call each provider once and log latency to runs.jsonl. Run FIRST: it shows what works today."""
import json, time
from pipeline.common import *
from pipeline.providers import gemini_tts, cf_image

def tts():
    lang = LANG(); sb = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
    model = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    wav = gemini_tts(sb["shots"][0]["narration"][lang], sb["narration"]["style_instruction"], sb["narration"]["voice"], model)
    p = OUT / "smoke" / f"sample_{lang}.wav"; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(wav)
    return model, {"lang": lang, "file": str(p)}

def image():
    model = os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-2-klein-4b")
    img = cf_image("a green seedling in dry earth, painterly, warm light", 1, model, 512, 512)
    p = OUT / "smoke" / "image.jpg"; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(img)
    return model, {"file": str(p)}

if __name__ == "__main__":
    load_env()
    for name, fn in [("tts", tts), ("image", image)]:
        t = time.time()
        try:
            model, params = fn(); log_run(f"smoke_{name}", model, None, params, None, time.time() - t); print(name, "OK", round(time.time() - t, 1), "s")
        except Exception as e:
            log_run(f"smoke_{name}", "?", None, {}, None, time.time() - t, 0, "error", str(e)[:200]); print(name, "FAILED:", str(e)[:300])
