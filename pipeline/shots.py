"""Stage: moving shots. Uses a Wan 2.2 clip (outputs/wan/shot_XX.mp4, made on Kaggle) if present,
otherwise a Ken Burns pan/zoom over the keyframe. Rendered per aspect ratio. Cached by input hash."""
import hashlib, time
from pipeline.common import *

ASPECTS = {"9x16": (1080, 1920), "16x9": (1920, 1080)}
FPS = 24

def fhash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.exists() else "none"

def kb_filter(camera, W, H, frames):
    # Smooth eased progress e in [0, 1], 3x oversampling, and unified warm-emerald film grade.
    e = f"0.5*(1-cos(PI*min(on/{frames},1)))"
    z = {
        "push_in": f"1+0.18*({e})",
        "pull_back": f"1.18-0.18*({e})",
        "pan_left": f"1.14+0.04*({e})",
        "pan_right": f"1.14+0.04*({e})",
        "pan_up": f"1.14+0.04*({e})",
        "pan_down": f"1.14+0.04*({e})",
        "static": f"1.02+0.05*({e})",
    }[camera]
    x = {
        "pan_left": f"(iw-iw/zoom)*(1-({e}))",
        "pan_right": f"(iw-iw/zoom)*({e})",
    }.get(camera, "iw/2-iw/zoom/2")
    y = {
        "pan_up": f"(ih-ih/zoom)*(1-({e}))",
        "pan_down": f"(ih-ih/zoom)*({e})",
    }.get(camera, "ih/2-ih/zoom/2")
    return (f"scale={W*3}:{H*3}:force_original_aspect_ratio=increase,crop={W*3}:{H*3},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
            f"eq=contrast=1.05:saturation=1.06,colorbalance=rs=0.02:gs=0.01:bs=-0.02,"
            f"vignette=PI/6,format=yuv420p")

def main(only=None):
    load_env()
    sb = load_storyboard()
    lang = LANG()
    shots_dir = OUT / "shots" / lang
    shots_dir.mkdir(parents=True, exist_ok=True)
    use_ws = bool(os.environ.get("WAVESPEED_API_KEY")) and os.environ.get("ENABLE_WAVESPEED") == "1"
    for s in sb["shots"]:
        if only and s["id"] != only: continue
        dur = shot_seconds(s)
        key = OUT / "keyframes" / f"shot_{s['id']}.jpg"
        wan = OUT / "wan" / f"shot_{s['id']}.mp4"
        if use_ws and not wan.exists() and key.exists():
            from pipeline.providers import wavespeed_wan_i2v
            wan.parent.mkdir(parents=True, exist_ok=True)
            t_ws = time.time()
            try:
                wan.write_bytes(wavespeed_wan_i2v(key, s["motion_prompt"], s["seed"], dur))
                log_run("wan", "wavespeed/wan-2.2-i2v-480p-ultra-fast", s["id"], {"dur": dur}, s["seed"], time.time() - t_ws, 0.05)
                print(f"shot {s['id']}: generated wan clip via WaveSpeed")
            except Exception as e:
                log_run("wan", "wavespeed/wan-2.2-i2v-480p-ultra-fast", s["id"], {"dur": dur}, s["seed"], time.time() - t_ws, 0, "error", str(e)[:200])
                print(f"shot {s['id']}: WaveSpeed failed ({e}); falling back to Ken Burns")
        src = "wan" if wan.exists() else "kenburns"
        if src == "kenburns" and not key.exists():
            print(f"shot {s['id']}: no keyframe yet, skipping"); continue
        for asp, (W, H) in ASPECTS.items():
            out = shots_dir / f"shot_{s['id']}_{asp}.mp4"
            d = digest(src, s["camera"], dur, asp, fhash(wan if src == "wan" else key))
            cache_key = f"shot:{lang}:{s['id']}:{asp}"
            if is_fresh(cache_key, d, out):
                print(f"shot {s['id']} {asp}: cached"); continue
            t = time.time()
            if src == "wan":
                vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration=10,format=yuv420p"
                ff(["-i", str(wan), "-vf", vf, "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "20", str(out)])
            else:
                ff(["-loop", "1", "-i", str(key), "-vf", kb_filter(s["camera"], W, H, int(round(dur * FPS))),
                    "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "20", str(out)])
            log_run("shots", f"ffmpeg-{src}", s["id"], {"aspect": asp, "lang": lang, "dur": dur, "camera": s["camera"]}, None, time.time() - t)
            mark(cache_key, d); print(f"shot {s['id']} {asp}: rendered ({src})")

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
