"""Stage: script. Validates `storyboard.json` and optionally drafts or translates story beats
via Gemini text API from a written family story brief (`--draft brief.txt`)."""
import argparse, json, os, time, requests
from pipeline.common import load_env, load_storyboard, log_run, retry, ROOT

GEMINI = "https://generativelanguage.googleapis.com/v1beta"


def draft_storyboard(brief_text, model):
    schema = (ROOT / "schema/storyboard.schema.json").read_text(encoding="utf-8")
    prompt = (
        "Turn the family story brief below into a valid JSON storyboard matching this JSON Schema.\n"
        "Include English (en), Amharic (am), and Afaan Oromoo (oro) narration lines, "
        "single-person Ethiopian character references, and clear `reason` fields.\n\n"
        f"Schema:\n{schema}\n\nBrief:\n{brief_text}"
    )
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
    r = requests.post(f"{GEMINI}/models/{model}:generateContent",
                      headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]}, json=body, timeout=180)
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])


def main():
    ap = argparse.ArgumentParser(description="Validate or draft storyboard.json from a brief.")
    ap.add_argument("--draft", help="Optional path to a plain-text story brief to draft storyboard.json")
    ap.add_argument("--out", default=str(ROOT / "storyboard.json"))
    args = ap.parse_args()
    load_env()
    if not args.draft:
        sb = load_storyboard()
        print(f"Contract OK: {sb['title']} / {sb.get('title_am', '')} ({len(sb['shots'])} shots)")
        return
    model = os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    t = time.time()
    sb = retry(lambda: draft_storyboard(open(args.draft, encoding="utf-8").read(), model))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(sb, f, indent=2, ensure_ascii=False)
    log_run("script", model, None, {"out": args.out}, None, time.time() - t)
    load_storyboard()
    print(f"Drafted and validated {args.out}")


if __name__ == "__main__":
    main()
