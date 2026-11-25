"""One-command cross-platform pipeline runner: `python -m pipeline.run [film|radio]`."""
import sys
from pipeline.common import load_env, load_storyboard
from pipeline import narration, keyframes, shots, music, assemble


def main(mode="film"):
    load_env()
    sb = load_storyboard()
    print(f"Validated: {sb['title']} ({len(sb['shots'])} shots)")
    narration.main()
    if mode == "radio":
        assemble.main("radio")
        return
    keyframes.main()
    shots.main()
    music.main()
    assemble.main("film")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "film")
