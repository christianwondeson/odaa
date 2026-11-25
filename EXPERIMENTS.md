# EXPERIMENTS (hypothesis -> change -> result; change ONE thing, fixed seed). Only log what you actually ran.
## E01 - TTS: does Afaan Oromoo come out intelligible?
Hypothesis: Gemini TTS auto-detects language without explicit Oromo listing, so phonetics on Afaan Oromoo names/ejections (`dh`, `q`, `ny`, `ch`) may drift.
Change: Ran `NARRATION_LANG=oro python -m pipeline.narration 01` and `07` (fell back to `gemini-2.5-flash-preview-tts`, voice `Kore`).
Result: Generated `outputs/narration/oro/shot_01.wav` (`8.33s`, latency `17.5s`, `runs.jsonl` 17:35:39) and `shot_07.wav` (`12.01s`, latency `20.05s`, `runs.jsonl` 17:36:04). Native Oromo speaker intelligibility rating (1–5) pending review.

## E02 - Oromo vs Amharic TTS (ceiling work: more languages)
Hypothesis: Amharic (officially listed on Gemini TTS) is more intelligible and natural than Afaan Oromoo under identical voice (`Kore`) and style instructions.
Change: Compared shots 01 and 07 across `NARRATION_LANG=am` vs `NARRATION_LANG=oro`.
Result: Both languages generated valid 24 kHz mono WAVs (`am` shot 01 `6.54s` vs `oro` `8.33s`; `am` shot 07 `12.84s` vs `oro` `12.01s`). Native listener preference & error audit (1–5) pending review in `ETHICS.md` / `EXPERIMENTS.md`.

## E03 - Single-portrait references (`ref_girl` + `ref_woman`) vs. 3-view turnaround sheet
Hypothesis: Replacing the 3-view turnaround `ref_girl` with single waist-up Ethiopian portraits (`ref_girl`, `ref_woman`) eliminates multi-clone pasting and prevents FLUX from rendering non-Ethiopian adults in later scenes.
Change: Split `references` in `storyboard.json` into single-portrait `ref_girl` and adult `ref_woman`, and added explicit per-reference labels in `pipeline/keyframes.py`.
Result: Eliminated cloned figures in `shot_05` and `shot_08` and replaced the non-Ethiopian woman/paper cup in `shot_09` with a consistent adult Ethiopian woman holding a clay cup (`runs.jsonl` keyframes 16:23, visual inspection of `outputs/keyframes/`).

## E04 - Scoping face directives out of botanical shots (`shot_01`, `shot_07`)
Hypothesis: Removing `"expressive Ethiopian East African faces"` from `style_block` when `refs` has no person stops FLUX from rendering faces on tree bark.
Change: Conditionalized `style` in `pipeline/keyframes.py` (`has_person`) and bumped `shot_01` seed (`2001 -> 2011`) with `"Pure botanical nature scene, tree bark and leaves only"`.
Result: Re-ran `python -m pipeline.keyframes shot_01` (`runs.jsonl`); tree trunk faces disappeared completely while keeping golden-hour seedling composition.

## E05 - Prompt wording fix for physical-labor washbasin (`shot_03`)
Hypothesis: Replacing `"reddened tired hands"` with `"weary soap-wet hands"` removes unintended blood-like coloration while keeping the strain of heavy laundry visible.
Change: Updated `shot_03` `image_prompt` and seed (`2003 -> 2013`) in `storyboard.json`, regenerated `shot_03` only.
Result: Clean soapy water and tired expression without red artifacts (`outputs/keyframes/shot_03.jpg`).

## E06 - Eased 3x-oversampled `zoompan` + `0.45s` `xfade` vs. 2x linear `concat`
Hypothesis: Cosine-eased `zoompan` at 3x oversampling, `pan_up`/`pan_down` axes, gentle breathing on static shots, and `0.45s` `xfade` dissolves reduce pixel jitter and make still-image shots feel animated while keeping exact sync.
Change: Updated `kb_filter()` in `pipeline/shots.py` and replaced `concat` with `tpad` + `xfade` in `pipeline/assemble.py`.
Result: All 20 clips (`274.89s` cumulative across baseline + v2) and both `9x16`/`16x9` films (`92.00s` exact) rendered cleanly with smooth transitions (`film_9x16.mp4` 35.5 MB, `film_16x9.mp4` 35.2 MB).

## E07 - `gemini-3.8-flash-tts` vs. `gemini-3.8-flash-lite-tts` under 10 RPD cap
Hypothesis: `gemini-3.8-flash-lite-tts` can complete Amharic narration seamlessly when `gemini-3.8-flash-tts` hits its 10 requests/day Free Tier limit.
Change: Added automatic daily-quota fallback in `pipeline/narration.py` (`FALLBACK_TTS=gemini-3.8-flash-lite-tts`).
Result: Shots 01–03 used `gemini-3.8-flash-tts`, shots 04–10 succeeded on `gemini-3.8-flash-lite-tts` (`7 ok, 88.63s` total in `runs.jsonl`).

## E08 - Pacing normalization (`NARRATION_TEMPO=1.22`, `pad=0.25`) to hit `60–90s` target
Hypothesis: Normalizing slow TTS phrasing (`1.22x` via FFmpeg `atempo` when not using `voice_override`) and tightening shot padding (`0.7s -> 0.25s`, end card `3s -> 2.5s`) brings total runtime under 90s without losing clarity.
Change: Added `narration_tempo()` in `pipeline/common.py` and `atempo` + softer low-passed placeholder pad (`650 Hz`) in `pipeline/assemble.py`.
Result: Runtime dropped from `109.33s` to `87.34s` (`radio_cut_am.mp4` `84.8s`, `film_9x16.mp4` & `film_16x9.mp4` `87.3s`), inside the `60–90s` target.

## Candidate experiments
Same prompt with/without the character block; 3 ACE-Step candidates; Wan vs Ken Burns on one shot; 4 vs 8 steps; open vs frontier keyframes (optional ceiling).
