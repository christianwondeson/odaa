"""A/B TTS benchmark across Gemini, Hasab AI, and Addis AI (Experiment E12).
Saves side-by-side WAVs to outputs/benchmarks/tts/<lang>/ without overwriting main narration."""
import argparse, time
from pipeline.common import OUT, audio_seconds, load_env, load_storyboard, log_run
from pipeline.narration import TTS_CHAIN, tts_call
from pipeline.providers import ADDIS_DEFAULT_VOICE, HASAB_DEFAULT_SPEAKER, addis_tts, hasab_tts
import os


def _run_provider(prov, text, lang, n_cfg, skip_gemini=False):
    if prov == "gemini":
        if skip_gemini:
            return None, None, "skipped (--skip-gemini)"
        primary = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
        models = [primary] + [m for m in TTS_CHAIN if m != primary]
        wav, used = tts_call(text, n_cfg["style_instruction"], n_cfg["voice"], models, set())
        return wav, used, None
    if prov == "hasab":
        if not os.environ.get("HASAB_API_KEY"):
            return None, None, "MISSING HASAB_API_KEY in .env"
        spk = os.environ.get("HASAB_TTS_SPEAKER") or HASAB_DEFAULT_SPEAKER.get(lang, "Selam")
        return hasab_tts(text, lang, spk), f"hasab:{spk}", None
    if prov == "addis":
        if not os.environ.get("ADDIS_API_KEY"):
            return None, None, "MISSING ADDIS_API_KEY in .env"
        vid = os.environ.get("ADDIS_TTS_VOICE") or ADDIS_DEFAULT_VOICE.get(lang, "am-hamen")
        return addis_tts(text, lang, vid), f"addis:{vid}", None
    return None, None, f"unknown provider {prov}"


def main():
    ap = argparse.ArgumentParser(description="Benchmark TTS clarity/latency across Gemini, Hasab AI, and Addis AI.")
    ap.add_argument("--lang", default=os.environ.get("NARRATION_LANG", "am"))
    ap.add_argument("--shots", nargs="+", default=["08", "09"])
    ap.add_argument("--providers", nargs="+", default=["hasab", "addis", "gemini"])
    ap.add_argument("--include-existing", action="store_true", help="Inspect already-generated narration/<lang>/shot_XX.wav timing too.")
    args = ap.parse_args()

    load_env()
    sb = load_storyboard()
    n_cfg = sb["narration"]
    by_id = {s["id"]: s for s in sb["shots"]}
    out_dir = OUT / "benchmarks" / "tts" / args.lang
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"TTS benchmark | lang={args.lang} | shots={args.shots} | providers={args.providers}")
    for sid in args.shots:
        shot = by_id[sid]
        text = shot["narration"][args.lang].strip()
        if args.include_existing:
            existing = OUT / "narration" / args.lang / f"shot_{sid}.wav"
            if existing.exists():
                print(f"  shot {sid} [existing] dur={audio_seconds(existing):.2f}s (min={shot['min_seconds']}s) -> {existing}")
        for prov in args.providers:
            t0 = time.time()
            try:
                wav, used, reason = _run_provider(prov, text, args.lang, n_cfg)
            except Exception as e:
                dt = time.time() - t0
                log_run("benchmark_tts", prov, sid, {"lang": args.lang}, None, dt, 0, "error", str(e)[:200])
                print(f"  shot {sid} [{prov}] ERROR ({dt:.2f}s): {str(e)[:180]}")
                continue
            if reason:
                print(f"  shot {sid} [{prov}] SKIPPED: {reason}")
                continue
            dt = time.time() - t0
            out = out_dir / f"shot_{sid}_{prov}.wav"
            out.write_bytes(wav)
            dur = audio_seconds(out)
            log_run("benchmark_tts", used, sid, {"lang": args.lang, "duration_s": round(dur, 2), "file": str(out)}, None, dt)
            print(f"  shot {sid} [{used}] OK latency={dt:.2f}s dur={dur:.2f}s (min={shot['min_seconds']}s) -> {out}")


if __name__ == "__main__":
    main()
