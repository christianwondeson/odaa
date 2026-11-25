"""Stage: moving shots. Uses a Wan 2.2 clip (outputs/wan/shot_XX.mp4, made on Kaggle) if present,
otherwise a Ken Burns pan/zoom over the keyframe. Rendered per aspect ratio. Cached by input hash."""
import hashlib, time
from pipeline.common import *

ASPECTS = {"9x16": (1080, 1920), "16x9": (1920, 1080)}
FPS = 24

def fhash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.exists() else "none"

def kb_filter(camera, W, H, frames):
    z = {"push_in": "min(1+0.0006*on,1.2)", "pull_back": "max(1.2-0.0006*on,1.0)",
         "pan_left": "1.15", "pan_right": "1.15", "static": "1.04"}[camera]
    x = {"pan_left": f"(iw-iw/zoom)*(1-on/{frames})", "pan_right": f"(iw-iw/zoom)*on/{frames}"}.get(camera, "iw/2-iw/zoom/2")
    return (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='{x}':y='ih/2-ih/zoom/2':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")

def main(only=None):
    sb = load_storyboard()
    (OUT / "shots").mkdir(parents=True, exist_ok=True)
    for s in sb["shots"]:
        if only and s["id"] != only: continue
        dur = shot_seconds(s)
        key = OUT / "keyframes" / f"shot_{s['id']}.jpg"
        wan = OUT / "wan" / f"shot_{s['id']}.mp4"
        src = "wan" if wan.exists() else "kenburns"
        if src == "kenburns" and not key.exists():
            print(f"shot {s['id']}: no keyframe yet, skipping"); continue
        for asp, (W, H) in ASPECTS.items():
            out = OUT / "shots" / f"shot_{s['id']}_{asp}.mp4"
            d = digest(src, s["camera"], dur, asp, fhash(wan if src == "wan" else key))
            if is_fresh(f"shot:{s['id']}:{asp}", d, out):
                print(f"shot {s['id']} {asp}: cached"); continue
            t = time.time()
            if src == "wan":
                vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration=10,format=yuv420p"
                ff(["-i", str(wan), "-vf", vf, "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "20", str(out)])
            else:
                ff(["-loop", "1", "-i", str(key), "-vf", kb_filter(s["camera"], W, H, int(dur * FPS)),
                    "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "20", str(out)])
            log_run("shots", f"ffmpeg-{src}", s["id"], {"aspect": asp, "dur": dur, "camera": s["camera"]}, None, time.time() - t)
            mark(f"shot:{s['id']}:{asp}", d); print(f"shot {s['id']} {asp}: rendered ({src})")

if __name__ == "__main__":
    import sys; main(sys.argv[1] if len(sys.argv) > 1 else None)
