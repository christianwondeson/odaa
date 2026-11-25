from pipeline.common import load_storyboard
sb = load_storyboard()
for L, info in sb["narration"]["languages"].items():
    w = sum(len(s["narration"].get(L, "").split()) for s in sb["shots"])
    print(f"  {L} ({info['name']}): {w} words, reviewed={info['reviewed']}")
mins = sum(s["min_seconds"] for s in sb["shots"])
print(f"OK: {len(sb['shots'])} shots, {mins}s minimum runtime")
if not all(i["reviewed"] for i in sb["narration"]["languages"].values()):
    print("WARNING: a narration language is not yet reviewed by a native speaker (set reviewed=true after review)")
