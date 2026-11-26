# FAILURES
Format: what broke | what I tried | what fixed it or the workaround. Log real blockers only (quota, memory, consistency, language).

## F01 - Afaan Oromoo is not on Gemini TTS's supported-language list (finding, 25 Nov 2026)
What I found: Google's speech-generation docs list Amharic, Tigrinya and Somali (Flash model) but I did not find Afaan Oromoo in the list. The model auto-detects language, so Oromo text may be read with the wrong phonetics.
Status: NOT yet tested. Next: run `make smoke NARRATION_LANG=oro`, have a native speaker rate it, and record the result here.
Plan: narrate the main film in Amharic (supported); keep Oromo as the documented experiment (E02) and keep Oromo in the visuals/proverb.

## F02 - Gemini 3.8 Flash TTS hit 429 Too Many Requests on shot 09 (25 Nov 2026)
What broke: Running `python -m pipeline.narration` sequentially after `smoke_test` generated shots 01–08 and failed on shot 09 with `429 Client Error: Too Many Requests` (`runs.jsonl`, 14:16:23), exhausting the per-minute free-tier RPM limit (~9 calls/min) beyond `retry()`'s 1s/2s backoff.
What fixed it: Waited ~60 seconds for the rate-limit window to reset and re-ran `python -m pipeline.narration`. Per-shot input-hash caching skipped shots 01–08 (`cached`) and generated shots 09–10 cleanly.

## F03 - Missing local FFmpeg, slow downloads, and non-elevated Chocolatey lock on Windows (25 Nov 2026)
What broke: `ffmpeg` (with `libass`) was missing on Windows. Automated `winget`, `curl`, and `pip install imageio-ffmpeg` downloads stalled at ~5–12 KB/s, and running `choco install ffmpeg -y` from a non-elevated shell failed with `Unable to obtain lock file access on 'C:\ProgramData\chocolatey\lib\...'`.
What fixed it: Initially bypassed `ffmpeg` in `pipeline.keyframes` by downscaling `ref_girl.jpg` and `ref_odaa.jpg` to `512x512` via Windows `.NET` (`System.Drawing`) and stitched a WAV preview (`outputs/work/radio_audio_am.wav`, 82.15 s). Resolved properly by running `choco install ffmpeg -y` in an Administrator `cmd` prompt, installing `ffmpeg` v9.1 essentials (`--enable-libass`, `--enable-libx264`).

## F04 - FFmpeg `subtitles=` filter failed on Windows drive-letter path in `pipeline/assemble.py` (25 Nov 2026)
What broke: Running `python -m pipeline.assemble film` crashed on `film_9x16.mp4` with `Unable to parse "original_size" option value "UserschrisDocumentsten-xodaaoutputsworksubs.srt" as image size` because `C:\...` backslashes were stripped and the `:` after `C` was parsed as an FFmpeg filter option delimiter.
What fixed it: Added `ff_path()` in `pipeline/assemble.py` to convert the resolved path to POSIX forward slashes, escape `:` as `\:`, and wrap it in single quotes (`'C\:/.../subs.srt'`). Re-running `python -m pipeline.assemble film` built both `film_9x16.mp4` and `film_16x9.mp4` cleanly.

## F05 - Gemini 3.8 Flash TTS hit 10 requests/day Free Tier cap + transient connection drop (25 Nov 2026)
What broke: When regenerating narration for the revised story, `gemini-3.8-flash-tts` stopped after shot 03 with `429 Rate limit exceeded (limit: 10 requests per day on Free Tier)` (`runs.jsonl`, 16:22–16:26). A subsequent fallback call on shot 07 hit `RemoteDisconnected`.
What fixed it: Added `tts_call()` in `pipeline/narration.py` to detect `"per day"` in `429` responses and automatically fall back to `gemini-3.8-flash-lite-tts` (`200 OK` on Amharic) while caching per-shot with `d_fallback` and pacing calls (`4s` sleep). Re-running resumed cleanly from shot 07 and completed shots 04–10.

## F06 - FLUX.2 klein visual drift: missing Ethiopian faces, foreign figures, turnaround cloning, and tree-trunk faces (25 Nov 2026)
What broke: On the first cut (`main`), (a) `ref_girl` was a 3-view turnaround sheet with text, causing FLUX to paste 2–3 cloned girls in `shot_05`/`08`, (b) shots `02`/`04`/`08`/`09` omitted Ethiopian facial features or hid faces, producing a European woman with a paper coffee cup in `shot_09` and a white hand in `shot_06`, (c) `"reddened tired hands"` in `shot_03` rendered like blood, and (d) adding `"expressive Ethiopian East African faces"` to global `style_block` caused faces to appear on the Odaa tree trunk in `shot_01`.
What fixed it: Replaced `ref_girl` with a single waist-up Ethiopian girl portrait, added a dedicated adult `ref_woman` portrait, scoped `style_block`/`character_block` per shot in `pipeline/keyframes.py` so botanical shots never receive face directives, replaced `"reddened"` with `"weary soap-wet hands"` in `shot_03`, and visually inspected all regenerated frames.

## F07 - Both 3.8 TTS models hit 10 RPD cap; `gemini-2.5-flash-preview-tts` API mismatch and slower pacing (25 Nov 2026)
What broke: On the revised 10-shot script, both `gemini-3.8-flash-tts` and `gemini-3.8-flash-lite-tts` hit `10 requests/day` Free Tier caps. Switching to `gemini-2.5-flash-preview-tts` via the 3.8 Interactions API returned `400 Speech annotations are not supported`, and via `generateContent` required an explicit `"Read aloud..."` prompt plus raw L16 PCM-to-WAV wrapping. Its slower speech rate also stretched total runtime to `106.3s` (`109.3s` with end card, above the `60–90s` target).
What fixed it: Added dual-endpoint support in `pipeline/providers.py` (`_pcm_to_wav` for 2.5 preview) and a 3-model fallback chain (`3.8-flash-tts` -> `3.8-flash-lite-tts` -> `2.5-flash-preview-tts`) in `pipeline/narration.py`, plus `outputs/voice_override/` support in `pipeline/common.py` and `pipeline/assemble.py` so human recordings can tighten pacing back to `60–90s`.

## F08 - `flux-1-schnell` rejected `/seed` (`400 Bad Request`) and 2.5 TTS occasional empty candidate on Oromo (25 Nov 2026)
What broke: (a) Calling `@cf/black-forest-labs/flux-1-schnell` with `"seed"` returned `400 AiError: Additional or unevaluated properties '/seed' at '/' not allowed`; (b) running `NARRATION_LANG=oro` on shot 02 returned an empty `candidates[0]` without `"content"`, raising `KeyError: 'content'` before all 3 TTS models hit daily `429` caps.
What fixed it: Removed `"seed"` from the `schnell` payload in `pipeline/providers.py` and added an explicit `parts` / `inlineData` check raising `RuntimeError` so `retry()` handles transient empty 2.5 TTS responses cleanly.

## F09 - Addis AI TTS rejected `/api/v1/voice/generations` with HTTP 422 `CLIENT_REQUEST_ID_REQUIRED` (26 Nov 2026)
What broke: Running `python -m pipeline.benchmark_tts --lang am --shots 08 09` after adding `ADDIS_API_KEY` returned `422 Client Error: Unprocessable Entity` (`runs.jsonl`, `benchmark_tts` `addis` 0.93s / 1.09s). Inspecting the live response body and catalog (`/api/v1/voice/voices`) showed `Addis Voices 2` requires `"client_request_id"` in the JSON payload (`CLIENT_REQUEST_ID_REQUIRED: client_request_id is required for paid generation`), even though some snippet examples omit it.
What fixed it: Updated `addis_tts()` in `pipeline/providers.py` to generate a UUID `client_request_id` (reused across retries in `pipeline/narration.py` for idempotency) and raise server error bodies on non-2xx responses. Re-running `pipeline.benchmark_tts` succeeded cleanly (`4/4` OK: `am` `08`/`09` in `3.57s`/`4.93s`; `oro` `01`/`06` in `3.49s`/`4.47s`).

## F10 - Extra third arm/hand anatomy artifact at `0:48` in `shot_06` (26 Nov 2026)
What broke: Playing back `film_9x16.mp4` around `0:48` (`shot_06`) revealed a third forearm/hand extending from behind the girl's crossed knees—triggered by the occluded pose `"sitting curled hugging her knees"` (`seed: 3106`).
What fixed it: Changed `shot_06` pose in `storyboard.json` to an unoccluded posture (`"leaning her back against the Odaa trunk, both hands resting cleanly on her closed worn blue notebook in her lap, exactly two arms and two natural hands visible"`, `seed: 3206`), regenerated `shot_06.jpg` cleanly, visually verified two natural arms/hands, and rebuilt `shot_06` clips plus all final `am`/`oro` MP4s.
