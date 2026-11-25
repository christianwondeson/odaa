"""Stage: keyframes via Cloudflare FLUX.2 klein. References first; each shot is conditioned on its reference images."""
import hashlib, time
from pipeline.common import *
from pipeline.providers import cf_image

def small_ref(name):
    """Downscale a reference to 512px (the API wants small inputs) and return its path."""
    src, dst = OUT / "keyframes" / f"{name}.jpg", OUT / "keyframes" / f"{name}_512.jpg"
    if src.exists() and (not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime):
        ff(["-i", str(src), "-vf", "scale=512:512:force_original_aspect_ratio=decrease", str(dst)])
    return dst

def main(only=None):
    load_env(); sb = load_storyboard()
    model = os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-2-klein-4b")
    W, H = int(os.environ.get("IMG_W", 1024)), int(os.environ.get("IMG_H", 1024))
    (OUT / "keyframes").mkdir(parents=True, exist_ok=True)
    jobs = [(r["id"], r["prompt"], r["seed"], []) for r in sb["references"]]
    for s in sb["shots"]:
        p = f"{sb['style_block']}. {sb['character_block']}. {s['image_prompt']}"
        if s.get("refs"):
            p = "Image 0 is the approved character/style reference; keep the same person and look. " + p
        jobs.append((f"shot_{s['id']}", p, s["seed"], s.get("refs", [])))
    for name, prompt, seed, refs in jobs:
        if only and name != only: continue
        paths = [small_ref(r) for r in refs if (OUT / "keyframes" / f"{r}.jpg").exists()]
        out = OUT / "keyframes" / f"{name}.jpg"
        d = digest(prompt, seed, model, W, H, [hashlib.sha256(p.read_bytes()).hexdigest()[:10] for p in paths])
        if is_fresh(f"keyframe:{name}", d, out):
            print(f"{name}: cached"); continue
        t = time.time()
        try:
            img = retry(lambda: cf_image(prompt[:2000], seed, model, W, H, paths))
        except Exception as e:
            log_run("keyframes", model, name, {"w": W, "h": H, "refs": refs}, seed, time.time() - t, 0, "error", str(e)[:200]); raise
        out.write_bytes(img)
        log_run("keyframes", model, name, {"w": W, "h": H, "refs": refs}, seed, time.time() - t)
        mark(f"keyframe:{name}", d); print(f"{name}: generated")

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
