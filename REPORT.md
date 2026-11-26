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

## 3. Experiments & What Changed Our Mind (`EXPERIMENTS.md`)
- **Character & Motif Consistency (`E03`–`E05`, `E11`):** Splitting a 3-view turnaround sheet into clean single portraits (`ref_girl`, `ref_woman`), scoping facial directives out of botanical shots (`F06`), fixing washbasin hand wording (`shot_03`), and threading `ref_odaa` across key beats eliminated cloned figures, non-Ethiopian drift, and bark faces.
- **Image Model Comparison (`E09`):** `@cf/black-forest-labs/flux-2-klein-4b` with `<=512px` portrait refs maintained character continuity (`~9.66s` avg across 51 runs) vs. `@cf/black-forest-labs/flux-1-schnell` (`flux-1-schnell` drifted to 2D cartoon in `shot_04` and 3-hand photorealism in `shot_10`).
- **Multilingual & Provider Benchmark (`E01`, `E02`, `E12`):** Full 10-shot cuts run in both Amharic (`88.74s`) and Afaan Oromoo (`89.88s`). Benchmarking Gemini vs. Hasab AI vs. Addis AI on `am` Shots `08`/`09` and `oro` Shots `01`/`06` showed local Ethiopian TTS APIs ran **2–6x faster** (`3.49s–4.95s` vs. `9.75s–31.39s` on Gemini) at natural speaking speed (`1.0x`, no `1.22x` acceleration needed).
- **Listener Choice (`E12`, `E13`):** Comparing Hasab AI, Addis AI, and Gemini TTS on real playback showed **Hasab AI** is more accurate on individual Amharic words, while **Gemini TTS** captivates the listener with stronger emotional storytelling cadence—so Gemini was kept for the film, alongside native-listener phrasing/model fixes on Shots `03` (`0:19`, "allowed her to live with her"), `05` (`0:33`), and `10` (`1:18` `ጥላ`). *(Still pending: formal `1–5` ratings from 3+ external listeners.)*

## 4. Reflection from Audience Tests (`DESIGN.md`, `TEST_PROTOCOL.md`)
- **User Test 1 — Radio Cut (3+ people):** `(TO FILL: date, who watched, exact observations on pacing/narration/Oromo vs Amharic clarity, and what lines changed in storyboard.json.)`
- **User Test 2 — Near-Final Cut (3+ people):** `(TO FILL: date, feedback on character consistency across shots, emotional ending under the Odaa tree, phone subtitle readability, and final edits made.)`

## 5. Costs, Measurement & Failures (`COSTS.md`, `FAILURES.md`)
- Measured across `363` logged calls in `runs.jsonl`: keyframes (`52/52` ok, `500.58s`), narration on Gemini (`46/53` ok across 3 models, `743.45s`), `benchmark_tts` across Hasab/Addis/Gemini (`18/20` ok, `132.01s`), local FFmpeg Ken Burns (`208/208` ok, `2258.75s`), and assembly (`26/26` ok, `2239.57s`).
- Documented `11` real blockers (`F01`–`F11`), including Gemini `10 RPD` exhaustion, Windows FFmpeg `ass=` colon escaping, FLUX turnaround cloning, `flux-1-schnell` schema rejection, Addis AI's undocumented `client_request_id` requirement (`422`), `shot_06`'s crossed-knee extra-arm artifact, and shared `outputs/shots/` truncation under `xfade`.
- **Kaggle GPU (`Wan 2.2` / `ACE-Step`):** `(TO FILL if run: GPU minutes, outputs/music/chosen.wav choice, Wan vs Ken Burns takeaway.)`

## 6. Ethics, Consent & Links (`ETHICS.md`)
- **Consent & Native Review:** `(TO FILL: date mother approved story inspiration; confirmation that `am` and `oro` scripts + proverb were reviewed and set `reviewed: true`.)`
- **Deliverable Links:**
  - Repository: https://github.com/christianwondeson/odaa
  - Walkthrough video: `(TO FILL)`
  - Public AI-labeled post: `(TO FILL)`
