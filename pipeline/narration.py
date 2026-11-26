"""Stage: narration. One WAV per shot per language via Gemini TTS, Hasab AI, or Addis AI. Cached per shot."""
import time, uuid, requests
from pipeline.common import *
from pipeline.providers import gemini_tts, hasab_tts, addis_tts, HASAB_DEFAULT_SPEAKER, ADDIS_DEFAULT_VOICE

TTS_CHAIN = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-2.5-flash-preview-tts"]


def tts_chain(primary):
    return [primary] + [m for m in TTS_CHAIN if m != primary]


def _shot_digest(text, n, lang, model_id):
    return digest(text, n["voice"], n["style_instruction"], lang, model_id)


def _synthesize_local_provider(provider, text, lang):
    if provider == "hasab":
        spk = os.environ.get("HASAB_TTS_SPEAKER") or HASAB_DEFAULT_SPEAKER.get(lang, "Selam")
        return retry(lambda: hasab_tts(text, lang, spk)), f"hasab:{spk}"
    if provider == "addis":
        vid = os.environ.get("ADDIS_TTS_VOICE") or ADDIS_DEFAULT_VOICE.get(lang, "am-hamen")
        req_id = str(uuid.uuid4())  # reuse idempotency key across retry attempts
        return retry(lambda: addis_tts(text, lang, vid, client_request_id=req_id)), f"addis:{vid}"
    raise ValueError(f"unknown TTS provider: {provider}")


def _cache_candidates(provider, primary_gemini, lang):
    if provider == "hasab":
        spk = os.environ.get("HASAB_TTS_SPEAKER") or HASAB_DEFAULT_SPEAKER.get(lang, "Selam")
        return [f"hasab:{spk}"]
    if provider == "addis":
        vid = os.environ.get("ADDIS_TTS_VOICE") or ADDIS_DEFAULT_VOICE.get(lang, "am-hamen")
        return [f"addis:{vid}"]
    cands = tts_chain(primary_gemini)
    if provider == "auto":
        local = []
        if os.environ.get("HASAB_API_KEY"):
            local += _cache_candidates("hasab", primary_gemini, lang)
        if os.environ.get("ADDIS_API_KEY"):
            local += _cache_candidates("addis", primary_gemini, lang)
        return local + cands
    return cands


def tts_call(text, style, voice, models, exhausted):
    """Try Gemini TTS models in order, skipping daily-exhausted ones and waiting briefly on RPM 429s."""
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
    provider = os.environ.get("TTS_PROVIDER", "gemini").strip().lower()
    primary = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
    models = tts_chain(primary)
    n = sb["narration"]; lang = LANG()
    (OUT / "narration" / lang).mkdir(parents=True, exist_ok=True)
    cache_models = _cache_candidates(provider, primary, lang)
    exhausted = set()
    for s in sb["shots"]:
        if only and s["id"] != only: continue
        out = OUT / "narration" / lang / f"shot_{s['id']}.wav"
        text = s["narration"][lang].strip()
        key = f"narration:{lang}:{s['id']}"
        if any(is_fresh(key, _shot_digest(text, n, lang, m), out) for m in cache_models):
            print(f"shot {s['id']}: cached"); continue
        t = time.time()
        try:
            if provider in ("hasab", "addis"):
                wav, used_model = _synthesize_local_provider(provider, text, lang)
            elif provider == "auto":
                local_order = [p for p, k in (("hasab", "HASAB_API_KEY"), ("addis", "ADDIS_API_KEY")) if os.environ.get(k)]
                wav = used_model = None
                for lp in local_order:
                    try:
                        wav, used_model = _synthesize_local_provider(lp, text, lang)
                        break
                    except Exception as e:
                        print(f"{lp} TTS failed ({e}); falling back...")
                if wav is None:
                    wav, used_model = tts_call(text, n["style_instruction"], n["voice"], models, exhausted)
            else:
                wav, used_model = tts_call(text, n["style_instruction"], n["voice"], models, exhausted)
        except Exception as e:
            log_run("narration", f"{provider}:{primary}", s["id"], {"lang": lang, "chars": len(text)}, None, time.time() - t, 0, "error", str(e)[:200]); raise
        out.write_bytes(wav)
        log_run("narration", used_model, s["id"], {"voice": n["voice"], "lang": lang, "chars": len(text), "provider": provider}, None, time.time() - t)
        mark(key, _shot_digest(text, n, lang, used_model))
        print(f"shot {s['id']}: generated ({used_model})")
        if used_model.startswith("gemini-"):
            time.sleep(4)  # pace calls to reduce AI Studio free-tier RPM 429s

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
