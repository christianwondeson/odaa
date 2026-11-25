"""Stage: narration. One WAV per shot per language via Gemini TTS. Cached by text+voice+style+model."""
import time, requests
from pipeline.common import *
from pipeline.providers import gemini_tts

TTS_CHAIN = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-2.5-flash-preview-tts"]


def tts_chain(primary):
    return [primary] + [m for m in TTS_CHAIN if m != primary]


def tts_call(text, style, voice, models, exhausted):
    """Try TTS models in order, skipping daily-exhausted ones and waiting briefly on RPM 429s."""
    candidates = [m for m in models if m not in exhausted] or models[-1:]
    for idx, active in enumerate(candidates):
        for wait_s in (20, 45):
            try:
                return retry(lambda: gemini_tts(text, style, voice, active)), active
            except requests.HTTPError as e:
                body = e.response.text if e.response is not None else ""
                code = e.response.status_code if e.response is not None else 0
                if code == 429 and "per day" not in body.lower():
                    print(f"rate limited (429 RPM on {active}); waiting {wait_s}s...")
                    time.sleep(wait_s)
                    continue
                if code in (404, 429, 503) and idx < len(candidates) - 1:
                    print(f"{active} unavailable/over quota ({code}); switching to {candidates[idx + 1]}")
                    exhausted.add(active)
                    break
                raise
    raise RuntimeError("all TTS models failed or exhausted")


def main(only=None):
    load_env(); sb = load_storyboard()
    primary = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    models = tts_chain(primary)
    n = sb["narration"]; lang = LANG()
    (OUT / "narration" / lang).mkdir(parents=True, exist_ok=True)
    exhausted = set()
    for s in sb["shots"]:
        if only and s["id"] != only: continue
        out = OUT / "narration" / lang / f"shot_{s['id']}.wav"
        text = s["narration"][lang].strip()
        key = f"narration:{lang}:{s['id']}"
        if any(is_fresh(key, digest(text, n["voice"], n["style_instruction"], lang, m), out) for m in models):
            print(f"shot {s['id']}: cached"); continue
        t = time.time()
        try:
            wav, used_model = tts_call(text, n["style_instruction"], n["voice"], models, exhausted)
        except Exception as e:
            log_run("narration", primary, s["id"], {"lang": lang, "chars": len(text)}, None, time.time() - t, 0, "error", str(e)[:200]); raise
        out.write_bytes(wav)
        log_run("narration", used_model, s["id"], {"voice": n["voice"], "lang": lang, "chars": len(text)}, None, time.time() - t)
        mark(key, digest(text, n["voice"], n["style_instruction"], lang, used_model))
        print(f"shot {s['id']}: generated ({used_model})")
        time.sleep(4)  # pace calls to reduce AI Studio free-tier RPM 429s

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
