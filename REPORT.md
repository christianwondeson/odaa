# Report — Under the Odaa (በኦዳ ዛፍ ሥር)

> **Submission status note:** All code, contract tests, API measurements, experiments `E01`–`E16`, failure logs `F01`–`F11`, walkthrough video, and public TikTok post below are grounded in repository logs (`runs.jsonl`, `outputs/benchmarks/`). Items still marked `(TO FILL)` reflect optional Kaggle GPU runs and `User Test 2` (`3+` phone viewers on the revised `88.12 s` / `11.84 MB` cut).

## 1. Story, Audience, and Why This Film Exists
- **Title:** *Under the Odaa / በኦዳ ዛፍ ሥር* (`9:16` vertical primary for WhatsApp/TikTok, plus `16:9` widescreen).
- **Audience & Intent (`DESIGN.md`):** Young Ethiopian women (ages 16–28) raised in blended or step-family households carrying silent duty and people-pleasing wounds, watching on a phone (*narrowed from broader "women and girls" after Tester 2 feedback*). Inspired by a real family story with mother's recorded consent (`26 Nov 2026`), stylized as fictional illustrated 35mm cinema.
- **Storyboard Contract (`storyboard.json`):** Every shot holds an explicit `reason`, reference list (`ref_girl`, `ref_woman`, `ref_odaa`), camera motion, bilingual narration (`am`, `oro`, `en`), and minimum duration floor validated against `schema/storyboard.schema.json`.

## 2. Architecture & Engineering Practice
- **Stage Isolation:** `python -m pipeline.run` orchestrates `validate -> narration -> keyframes -> shots -> music -> assemble` around `storyboard.json` and SHA-256 input hashing (`outputs/.cache.json`). Re-running after editing a single shot regenerates only that shot.
- **Quotas & Fallbacks (`pipeline/providers.py`, `pipeline/narration.py`):**
  - Default `TTS_PROVIDER=gemini` automatically detects Free Tier `429` daily limits (`10 RPD`) and steps across `gemini-3.8-flash-tts` -> `gemini-3.8-flash-lite-tts` -> `gemini-2.5-flash-preview-tts` (handling both Interactions API WAV and `generateContent` raw PCM-to-WAV).
  - Optional Ethiopian-native `TTS_PROVIDER=hasab|addis|auto` routes narration through Hasab AI (`Selam`/`Lemlem`) or Addis AI (`am-hamen`/`om-ayyaantuu`), and `outputs/voice_override/<lang>/` prioritizes real human recordings at `1.0x` tempo.
  - Visuals and music swap cleanly between Kaggle GPU outputs (`outputs/wan/`, `outputs/music/chosen.wav`) and deterministic local FFmpeg fallbacks (3x oversampled cosine-eased Ken Burns + `-14 LUFS` `loudnorm` + `sidechaincompress` ducking).

## 3. Practices Tested Honestly (Suggested Practices vs. Instinct — `10 pts`)
- **Practice that beat instinct — Single waist-up portrait refs + per-stage caching (`E03`, `E08`):** Building a strict JSON Schema contract + SHA-256 input cache (`outputs/.cache.json`) and splitting `ref_girl` and `ref_woman` into single waist-up portraits felt slower upfront than prompting scenes straight away. In practice, it saved hours during `E13` and `F10` (regenerating Shot `03`/`05`/`10` narration and `shot_06` keyframe cleanly without touching the other 9 shots) and eliminated non-Ethiopian adult drift in `shot_09`.
- **Practice that did NOT work as assumed — Multi-view turnaround sheet & global style-block faces (`F06`, `E03`, `E04`):** Prompting a classic 3-view character turnaround sheet (`ref_girl`) and putting `"expressive Ethiopian East African faces"` in the global `style_block` backfired on FLUX.2 klein: FLUX pasted 2–3 cloned figures into `shot_05`/`shot_08` and rendered human faces onto the Odaa tree trunk in `shot_01`. Fixing both required removing text/multi-views from references and conditioning face directives only on shots containing people.

## 4. Reflection & Learning from Audience + Listener Passes (`10 pts`)
- **Hardest technical problem & solution (`F11`, `F05`, `F07`, `F09`):** Solving silent FFmpeg `xfade` stream truncation at `62.75 s` (`1:02.75`) when `am` and `oro` shared `outputs/shots/`, plus surviving `10 RPD` Gemini TTS caps via a 3-model endpoint chain (`Interactions` WAV vs `generateContent` PCM) and uncovering Addis AI's undocumented `client_request_id` requirement (`422`).
- **Native Amharic Listener Pass (`E12`, `E13`):** Real playback flagged three exact issues: Shot `03` (`0:19`, `"called her"` -> updated to `"ከሷ ጋር እንድትኖር ስትፈቅድላት"` / *"allowed her to live with her"*), Shot `05` (`0:33`, dense `የታናናሾቿን` -> simplified to `የታናናሽ ልጆቹን`), and Shot `10` (`1:18`, `ጥላ` mispronounced on `2.5-preview` -> regenerated on `3.8-flash-lite-tts`). Comparing providers showed **Hasab AI** pronounced words more accurately, while **Gemini TTS** delivered warmer storytelling cadence (`Gemini` selected for final film).
- **User Test 1 — Early Cut (`3/3` logged in `DESIGN.md`, `E15`, `E16`):**
  - *Tester 1* understood the plot cleanly and remembered the mother-past line, but felt only *"a tiny bit of pity"*, noted *"the AI voice was kind of funny"*, and missed the takeaway message.
  - *Tester 2* urged narrowing the target audience for greater depth while encouraging the opening Odaa tree and seed line.
  - *Tester 3* appreciated the core respect-for-women message, but felt the story felt generic in places and lacked emotional depth & a smooth age/craft transition between being a young child and an adult designer.
  - **Changes made directly from them:** (1) narrowed target audience in `DESIGN.md` to young Ethiopian women (16–28) in blended/step-family households; (2) added an explicit self-rescue turning point to Shot `07` (*"So she chose to save herself..."*) and closed Shot `10` back on the Shot `01` seed & Odaa shelter; (3) rewrote **Shot `08`** into an explicit child-to-adult craft transition (*"Years passed; working by day and studying traditional patterns in her blue notebook by night, her hidden roots grew deep"*) while keeping total runtimes inside `60–90 s` (`88.12 s` Amharic / `88.74 s` Oromo).
- **User Test 2 — Near-Final Cut (3+ people, `DESIGN.md`):** `(TO FILL: date, 3+ people watching film_9x16.mp4 on phones, feedback on girl consistency across shots, ending under the Odaa tree, subtitle legibility, and final tweaks made.)`

## 5. Curiosity Beyond the Floor (`10 pts`)
- **Extra Language (`E01`, `E02`):** Built complete bilingual `storyboard.json`, narration WAVs, subtitles (`am+en` and `oro+en`), radio cuts, and `9:16` / `16:9` MP4s in **Afaan Oromoo** (`88.74 s`, `mobile` `12.08 MB`) alongside **Amharic** (`88.12 s`, `mobile` `11.84 MB`), proving empirically where general TTS lacks Oromo support (`F01`).
- **Two Real Model Benchmarks (`E09`, `E12`):**
  - *Image (`E09`):* `@cf/black-forest-labs/flux-2-klein-4b` with `<=512px` portrait refs held character identity cleanly (`~9.6s`/img) vs. `@cf/black-forest-labs/flux-1-schnell` (`4` steps, no refs -> drifted to 2D cartoon in `shot_04` and 3-hand photorealism in `shot_10`).
  - *Speech (`E12`):* Benchmarked **Gemini TTS** vs. **Hasab AI** (`Selam`/`Lemlem`, `3.80–4.95 s`) vs. **Addis AI** (`am-hamen`/`om-ayyaantuu`, `3.49–4.93 s`) across both `am` (`08`/`09`) and `oro` (`01`/`06`), saving all 10 side-by-side WAVs in `outputs/benchmarks/tts/`.
- **Agent Tooling (`E10`):** Packaged validation, shot inspection, single-shot regeneration, and `build_film` as an **MCP Server** ([pipeline/mcp_server.py](pipeline/mcp_server.py)) so any coding agent can operate the studio cleanly.

## 6. Costs, Measurement & Failures (`COSTS.md`, `FAILURES.md`)
- Measured across `455` logged calls in `runs.jsonl`: keyframes (`52/52` ok, `500.58s`), narration on Gemini (`52/59` ok across 3 models, `841.89s`), `benchmark_tts` across Hasab/Addis/Gemini (`18/20` ok, `132.01s`), local FFmpeg Ken Burns (`268/268` ok, `2854.83s`), `assemble` (`43/43` ok, `3362.40s`), and `720p` mobile exports (`9/9` ok, `184.99s`).
- Documented `11` real blockers (`F01`–`F11`), including Gemini `10 RPD` exhaustion, Windows FFmpeg `ass=` colon escaping, FLUX turnaround cloning, `flux-1-schnell` schema rejection, Addis AI's undocumented `client_request_id` requirement (`422`), `shot_06`'s crossed-knee extra-arm artifact, and shared `outputs/shots/` truncation under `xfade`.
- **Kaggle GPU (`Wan 2.2` / `ACE-Step`):** `(TO FILL if run: GPU minutes, outputs/music/chosen.wav choice, Wan vs Ken Burns takeaway.)`

## 7. What I Would Build Next
1. **Replace synthetic TTS comedy with hybrid human/local-AI voice (`outputs/voice_override/`):** Pair Hasab AI's cleaner Amharic/Oromo pronunciation with either a real voice actor or mother's narrated read so listeners feel deeper emotional warmth instead of "funny" synthetic inflection.
2. **Swap placeholder score & still motion for Kaggle `ACE-Step 1.5` + `Wan 2.2`:** Render three acoustic *krar*/string score candidates (`chosen.wav`) and animate hero emotional beats (`04`, `06`, `07`, `10`) with Wan 2.2 TI2V-5B, then run a 5-person blind preference test on `E09`.
3. **Zero-code web studio & showcase:** Deploy a Next.js + Vercel screening room for family reviewers with language/aspect toggles (`9:16`, `16:9`, `radio_cut`) and drag-and-drop preview uploads backed by the pipeline's MCP server (`pipeline/mcp_server.py`).

## 8. Ethics, Consent & Links (`ETHICS.md`)
- **Consent & Native Review:** Mother informed and consented directly on `26 Nov 2026` (private consent record kept offline, not published); Amharic script reviewed across `E12`, `E13`, `E15`, `E16` (`am`: `reviewed=true`); Afaan Oromoo (`oro`) & Odaa proverb remain `reviewed=false` pending an independent fluent Oromo audit.
- **Deliverable Links:**
  - Repository: https://github.com/christianwondeson/odaa
  - Walkthrough video: https://www.loom.com/share/74fdf0861cd84ae39ee8b21a953050e6
  - Public AI-labeled post: https://www.tiktok.com/@christianwondeson/video/7712532010245360902
