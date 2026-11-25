"""Report which credentials are set (never prints their values)."""
from pipeline.common import *
load_env()
need = {"GEMINI_API_KEY": "Google AI Studio key (TTS, script help)", "CF_ACCOUNT_ID": "Cloudflare account id", "CF_API_TOKEN": "Cloudflare API token (Workers AI)"}
bad = 0
for k, why in need.items():
    ok = bool(os.environ.get(k)); bad += not ok
    print(("OK      " if ok else "MISSING ") + f"{k:15} {why}")
print("TTS model:  ", os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts (default)"))
print("Image model:", os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-2-klein-4b (default)"))
print("Language:   ", LANG())
raise SystemExit(1 if bad else 0)
