# FAILURES
Format: what broke | what I tried | what fixed it or the workaround. Log real blockers only (quota, memory, consistency, language).

## F01 - Afaan Oromoo is not on Gemini TTS's supported-language list (finding, 25 Nov 2026)
What I found: Google's speech-generation docs list Amharic, Tigrinya and Somali (Flash model) but I did not find Afaan Oromoo in the list. The model auto-detects language, so Oromo text may be read with the wrong phonetics.
Status: NOT yet tested. Next: run `make smoke NARRATION_LANG=oro`, have a native speaker rate it, and record the result here.
Plan: narrate the main film in Amharic (supported); keep Oromo as the documented experiment (E02) and keep Oromo in the visuals/proverb.

## F02 - Gemini 3.8 Flash TTS hit 429 Too Many Requests on shot 09 (25 Nov 2026)
What broke: Running `python -m pipeline.narration` sequentially after `smoke_test` generated shots 01–08 and failed on shot 09 with `429 Client Error: Too Many Requests` (`runs.jsonl`, 14:16:23), exhausting the per-minute free-tier RPM limit (~9 calls/min) beyond `retry()`'s 1s/2s backoff.
What fixed it: Waited ~60 seconds for the rate-limit window to reset and re-ran `python -m pipeline.narration`. Per-shot input-hash caching skipped shots 01–08 (`cached`) and generated shots 09–10 cleanly.

## F03 - Missing local FFmpeg stalled `shots` and `assemble` on Windows (25 Nov 2026)
What broke: `ffmpeg` (with `libass`) was not installed on Windows, and downloading `Gyan.FFmpeg` / `imageio-ffmpeg` stalled at ~5–12 KB/s on the local connection.
Workaround so far: Downscaled `ref_girl.jpg` and `ref_odaa.jpg` to `512x512` with Windows `.NET` (`System.Drawing`) so `pipeline.keyframes` could generate all 10 shot keyframes, and stitched a timed WAV preview (`outputs/work/radio_audio_am.wav`, 82.15 s) with Python's `wave` module. Full `shots` (Ken Burns) and `assemble` (`radio_cut_am.mp4`, `film_9x16.mp4`, `film_16x9.mp4`) remain blocked until `ffmpeg` is installed.
