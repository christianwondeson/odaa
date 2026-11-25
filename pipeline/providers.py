"""All third-party API calls live here, so a model change touches one file."""
import base64, os, requests

GEMINI = "https://generativelanguage.googleapis.com/v1beta"


def gemini_tts(text, style, voice, model):
    """Gemini 3.8 TTS via the Interactions API. `text` is a VERBATIM transcript (no stage directions);
    delivery goes in speech_metadata.style. Language is auto-detected. Returns WAV bytes (24 kHz mono, RIFF header)."""
    body = {"model": model,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    r = requests.post(f"{GEMINI}/interactions", headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=body, timeout=180)
    r.raise_for_status()
    audio = [c for st in r.json().get("steps", []) if st.get("type") == "model_output"
             for c in st.get("content", []) if c.get("type") == "audio"]
    if not audio:
        raise RuntimeError("no audio block in response: " + r.text[:300])
    wav = base64.b64decode(audio[-1]["data"])
    if wav[:4] != b"RIFF":
        raise RuntimeError("expected WAV (RIFF) bytes; got something else")
    return wav


def cf_image(prompt, seed, model, width=1024, height=1024, ref_paths=()):
    """Cloudflare Workers AI image. FLUX.2 klein takes multipart form data; up to 4 reference images (keep them small)."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{model}"
    hdr = {"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}"}
    if "schnell" in model:  # FLUX.1 schnell: JSON in, no reference images
        r = requests.post(url, headers=hdr, json={"prompt": prompt, "steps": 4, "seed": seed}, timeout=180)
        r.raise_for_status(); return base64.b64decode(r.json()["result"]["image"])
    fields = {"prompt": (None, prompt), "seed": (None, str(seed)), "width": (None, str(width)), "height": (None, str(height))}
    for i, p in enumerate(list(ref_paths)[:4]):
        fields[f"input_image_{i}"] = (os.path.basename(p), open(p, "rb").read(), "image/jpeg")
    r = requests.post(url, headers=hdr, files=fields, timeout=180)
    r.raise_for_status()
    if r.headers.get("content-type", "").startswith("image/"):
        return r.content
    j = r.json()
    img = (j.get("result") or j).get("image")
    if not img:
        raise RuntimeError("no image in response: " + r.text[:300])
    return base64.b64decode(img)
