"""MCP server exposing the Under the Odaa short-film pipeline to coding agents and tools.
Run over stdio: `python -m pipeline.mcp_server` (requires `mcp>=2`)."""
from mcp.server.mcpserver import MCPServer
from pipeline.common import load_env, load_storyboard, shot_seconds, OUT, LANG
from pipeline import narration, keyframes, shots, run as runner

mcp = MCPServer("odaa")


@mcp.tool()
def validate_storyboard() -> dict:
    """Validate storyboard.json against its JSON Schema and return summary metadata."""
    sb = load_storyboard()
    return {
        "title": sb["title"],
        "title_am": sb.get("title_am", ""),
        "shots": len(sb["shots"]),
        "total_seconds": round(sum(shot_seconds(s) for s in sb["shots"]) + sb["end_card"]["seconds"], 2),
        "languages": {k: v["reviewed"] for k, v in sb["narration"]["languages"].items()},
    }


@mcp.tool()
def list_shots() -> list[dict]:
    """List every storyboard shot with its reason, camera, references, and artifact status."""
    sb = load_storyboard()
    lang = LANG()
    return [
        {
            "id": s["id"],
            "reason": s["reason"],
            "camera": s["camera"],
            "refs": s.get("refs", []),
            "has_narration": (OUT / "narration" / lang / f"shot_{s['id']}.wav").exists(),
            "has_keyframe": (OUT / "keyframes" / f"shot_{s['id']}.jpg").exists(),
            "has_clip_9x16": (OUT / "shots" / f"shot_{s['id']}_9x16.mp4").exists(),
        }
        for s in sb["shots"]
    ]


@mcp.tool()
def regenerate_shot(shot_id: str, stage: str = "all") -> dict:
    """Regenerate a single shot across narration, keyframes, shots, or all stages."""
    load_env()
    load_storyboard()
    if stage in ("narration", "all"):
        narration.main(only=shot_id)
    if stage in ("keyframes", "all"):
        keyframes.main(only=f"shot_{shot_id}")
    if stage in ("shots", "all"):
        shots.main(only=shot_id)
    return {"shot_id": shot_id, "stage": stage, "status": "ok"}


@mcp.tool()
def build_film(mode: str = "film") -> dict:
    """Run the full one-command pipeline (`film` or `radio`) from storyboard.json."""
    if mode not in ("film", "radio"):
        raise ValueError("mode must be 'film' or 'radio'")
    runner.main(mode=mode)
    return {"mode": mode, "final_dir": str(OUT / "final")}


if __name__ == "__main__":
    mcp.run()
