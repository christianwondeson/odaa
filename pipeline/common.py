"""Shared helpers: contract validation, input hashing, per-shot cache, retries, run log."""
import hashlib, json, os, pathlib, subprocess, time, wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
RUNS = ROOT / "runs.jsonl"
CACHE = OUT / ".cache.json"


def load_env():
    """Read .env (never committed) into os.environ."""
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_storyboard():
    """Validate against the schema on EVERY run; abort on failure."""
    from jsonschema import validate
    sb = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
    validate(sb, json.loads((ROOT / "schema/storyboard.schema.json").read_text()))
    return sb


def digest(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def is_fresh(key, dig, outfile):
    return _cache().get(key) == dig and pathlib.Path(outfile).exists()


def mark(key, dig):
    c = _cache(); c[key] = dig
    OUT.mkdir(exist_ok=True); CACHE.write_text(json.dumps(c, indent=1))


def log_run(stage, model, shot=None, params=None, seed=None, latency_s=None,
            cost_usd=0.0, status="ok", note=""):
    rec = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S"), stage=stage, model=model, shot=shot,
               params=params or {}, seed=seed, latency_s=round(latency_s or 0, 2),
               cost_usd=cost_usd, status=status, note=note)
    with open(RUNS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def retry(fn, tries=3, base=2.0):
    """Exponential backoff. Re-raises the last error so callers can fall back."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa
            if i == tries - 1:
                raise
            time.sleep(base ** i)


def audio_seconds(path):
    p = pathlib.Path(path)
    if p.suffix.lower() == ".wav":
        with wave.open(str(p), "rb") as w:
            return w.getnframes() / w.getframerate()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0.0


def narration_audio_path(shot_id):
    """Prefer an optional human voice override in outputs/voice_override/ if present, else generated TTS."""
    override_dir = OUT / "voice_override"
    for ext in (".wav", ".mp3", ".m4a", ".ogg"):
        cand = override_dir / f"shot_{shot_id}{ext}"
        if cand.exists():
            return cand
    return OUT / "narration" / LANG() / f"shot_{shot_id}.wav"


def narration_tempo(shot_id):
    """Keep human voice overrides at 1.0x; normalize slow TTS phrasing to fit 60-90s."""
    override_dir = OUT / "voice_override"
    if any((override_dir / f"shot_{shot_id}{ext}").exists() for ext in (".wav", ".mp3", ".m4a", ".ogg")):
        return 1.0
    return float(os.environ.get("NARRATION_TEMPO", "1.22"))


LANG = lambda: os.environ.get("NARRATION_LANG", "am")


def shot_seconds(shot, pad=0.25):
    """Shot length = narration length + pad, never below the storyboard minimum.
    The narration sets the timing, as in a professional cut."""
    aud = narration_audio_path(shot["id"])
    tempo = narration_tempo(shot["id"])
    n = (audio_seconds(aud) / tempo) + pad if aud.exists() else 0
    return round(max(shot["min_seconds"], n), 2)


def ff(args):
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args,
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
