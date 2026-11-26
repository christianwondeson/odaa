# Report — Under the Odaa (በኦዳ ዛፍ ሥር)

> **Submission status note:** All code, contract tests, API measurements, experiments `E01`–`E13`, and failure logs `F01`–`F11` below are grounded in repository logs (`runs.jsonl`, `outputs/benchmarks/`). Sections marked `(TO FILL)` require real human listening/testing, consent confirmation, optional Kaggle GPU outputs, and final publish links before submission.

## 1. Story, Audience, and Why This Film Exists
- **Title:** *Under the Odaa / በኦዳ ዛፍ ሥር* (`9:16` vertical primary for WhatsApp/TikTok, plus `16:9` widescreen).
- **Audience & Intent (`DESIGN.md`):** Women and girls of my generation (and their families) watching on a phone. Inspired by a real family story, stylized as fictional illustrated 35mm cinema so no private relative is identified without consent.
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
- **User Test 1 — Radio Cut (3+ people, `DESIGN.md`):** `(TO FILL: date, 3+ names/roles from target audience, verbatim feedback on pacing/emotion/clarity, and exact lines changed in storyboard.json.)`
- **User Test 2 — Near-Final Cut (3+ people, `DESIGN.md`):** `(TO FILL: date, 3+ people watching film_9x16.mp4 on phones, feedback on girl consistency across shots, ending under the Odaa tree, subtitle legibility, and final tweaks made.)`

## 5. Curiosity Beyond the Floor (`10 pts`)
- **Extra Language (`E01`, `E02`):** Built complete bilingual `storyboard.json`, narration WAVs, subtitles (`am+en` and `oro+en`), radio cuts, and `9:16` / `16:9` MP4s in **Afaan Oromoo** (`89.88 s`) alongside **Amharic** (`88.74 s`), proving empirically where general TTS lacks Oromo support (`F01`).
- **Two Real Model Benchmarks (`E09`, `E12`):**
  - *Image (`E09`):* `@cf/black-forest-labs/flux-2-klein-4b` with `<=512px` portrait refs held character identity cleanly (`~9.6s`/img) vs. `@cf/black-forest-labs/flux-1-schnell` (`4` steps, no refs -> drifted to 2D cartoon in `shot_04` and 3-hand photorealism in `shot_10`).
  - *Speech (`E12`):* Benchmarked **Gemini TTS** vs. **Hasab AI** (`Selam`/`Lemlem`, `3.80–4.95 s`) vs. **Addis AI** (`am-hamen`/`om-ayyaantuu`, `3.49–4.93 s`) across both `am` (`08`/`09`) and `oro` (`01`/`06`), saving all 10 side-by-side WAVs in `outputs/benchmarks/tts/`.
- **Agent Tooling (`E10`):** Packaged validation, shot inspection, single-shot regeneration, and `build_film` as an **MCP Server** ([pipeline/mcp_server.py](pipeline/mcp_server.py)) so any coding agent can operate the studio cleanly.

## 6. Costs, Measurement & Failures (`COSTS.md`, `FAILURES.md`)
- Measured across `363` logged calls in `runs.jsonl`: keyframes (`52/52` ok, `500.58s`), narration on Gemini (`46/53` ok across 3 models, `743.45s`), `benchmark_tts` across Hasab/Addis/Gemini (`18/20` ok, `132.01s`), local FFmpeg Ken Burns (`208/208` ok, `2258.75s`), and assembly (`26/26` ok, `2239.57s`).
- Documented `11` real blockers (`F01`–`F11`), including Gemini `10 RPD` exhaustion, Windows FFmpeg `ass=` colon escaping, FLUX turnaround cloning, `flux-1-schnell` schema rejection, Addis AI's undocumented `client_request_id` requirement (`422`), `shot_06`'s crossed-knee extra-arm artifact, and shared `outputs/shots/` truncation under `xfade`.
- **Kaggle GPU (`Wan 2.2` / `ACE-Step`):** `(TO FILL if run: GPU minutes, outputs/music/chosen.wav choice, Wan vs Ken Burns takeaway.)`

## 7. Ethics, Consent & Links (`ETHICS.md`)
- **Consent & Native Review:** `(TO FILL: date mother approved story inspiration; confirmation that `am` and `oro` scripts + proverb were reviewed and set `reviewed: true`.)`
- **Deliverable Links:**
  - Repository: https://github.com/christianwondeson/odaa
  - Walkthrough video: `(TO FILL)`
  - Public AI-labeled post: `(TO FILL)`
