"""All third-party API calls live here, so a model change touches one file."""
import base64, io, os, requests, time, wave

GEMINI = "https://generativelanguage.googleapis.com/v1beta"
WAVESPEED = "https://api.wavespeed.ai/api/v3"


def _pcm_to_wav(pcm, rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def gemini_tts(text, style, voice, model):
    """Gemini TTS supporting both 3.8 Interactions API and 2.5 preview generateContent API.
    Returns WAV bytes (24 kHz mono, RIFF header)."""
    hdr = {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}
    if "2.5" in model:
        body = {"contents": [{"parts": [{"text": f"Read aloud in a {style} tone:\n\n{text}"}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        r = requests.post(f"{GEMINI}/models/{model}:generateContent", headers=hdr, json=body, timeout=180)
        r.raise_for_status()
        cand = (r.json().get("candidates") or [{}])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        if not parts or "inlineData" not in parts[0]:
            raise RuntimeError(f"no audio content in 2.5 TTS response: {cand}")
        part = parts[0]["inlineData"]
        raw = base64.b64decode(part["data"])
        return raw if raw[:4] == b"RIFF" else _pcm_to_wav(raw)
    body = {"model": model,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
                       "annotations": [{"type": "speech_metadata", "style": style}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]}}
    r = requests.post(f"{GEMINI}/interactions", headers=hdr, json=body, timeout=180)
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
    if "schnell" in model:  # FLUX.1 schnell: JSON in, no reference images, /seed rejected by Workers AI schema
        r = requests.post(url, headers=hdr, json={"prompt": prompt, "steps": 4}, timeout=180)
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


def _wavespeed_run(model_path, payload, timeout_s=360):
    """Submit a WaveSpeed async task, poll until completed, and download the first output bytes."""
    hdr = {"Authorization": f"Bearer {os.environ['WAVESPEED_API_KEY']}", "Content-Type": "application/json"}
    r = requests.post(f"{WAVESPEED}/{model_path}", headers=hdr, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json().get("data") or r.json()
    task_id = data["id"]
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        p = requests.get(f"{WAVESPEED}/predictions/{task_id}/result", headers=hdr, timeout=30)
        p.raise_for_status()
        res = p.json().get("data") or p.json()
        st = res.get("status")
        if st == "completed" and res.get("outputs"):
            dl = requests.get(res["outputs"][0], timeout=120)
            dl.raise_for_status()
            return dl.content
        if st == "failed":
            raise RuntimeError(f"WaveSpeed task {task_id} failed: {res.get('error')}")
        time.sleep(3)
    raise TimeoutError(f"WaveSpeed task {task_id} timed out after {timeout_s}s")


def wavespeed_wan_i2v(image_path, motion_prompt, seed, duration=5):
    """Generate a 480p Wan 2.2 image-to-video clip via WaveSpeed."""
    b64 = base64.b64encode(open(image_path, "rb").read()).decode("ascii")
    payload = {
        "image": f"data:image/jpeg;base64,{b64}",
        "prompt": motion_prompt,
        "duration": 5 if duration <= 6 else 8,
        "negative_prompt": "blurry, distorted face, extra limbs, flicker, text, watermark",
        "seed": seed,
        "enable_sync_mode": False,
    }
    return _wavespeed_run("wavespeed-ai/wan-2.2/i2v-480p-ultra-fast", payload)


def wavespeed_acestep(tags, duration=60, seed=42):
    """Generate an instrumental ACE-Step 1.5 track via WaveSpeed."""
    payload = {"tags": tags, "lyrics": "", "duration": duration, "seed": seed}
    return _wavespeed_run("wavespeed-ai/ace-step-1.5", payload)
