# COSTS
Measure from runs.jsonl: latency per stage, GPU minutes (Kaggle), free-tier limits as found today, list-price equivalent.
| Stage | Calls | Total latency | GPU min | List-price equiv. |
|---|---|---|---|---|
| smoke_tts (`gemini-3.8-flash-tts`) | 1 (1 ok) | 6.71 s | 0 | $0.00 (AI Studio free tier) |
| smoke_image (`@cf/black-forest-labs/flux-2-klein-4b`) | 1 (1 ok) | 7.86 s | 0 | $0.00 (Cloudflare free tier) |
| narration (`am`, `gemini-3.8-flash-tts`) | 19 (14 ok, 5 err) | 356.12 s | 0 | $0.00 (10 RPD cap; ~$0.002/10s list) |
| narration (`am`, `gemini-3.8-flash-lite-tts`) | 13 (13 ok) | 145.65 s | 0 | $0.00 (10 RPD cap; ~$0.0015/10s list) |
| narration (`am` + `oro` test, `gemini-2.5-flash-preview-tts`) | 5 (5 ok) | 65.08 s | 0 | $0.00 (AI Studio free tier) |
| keyframes (`@cf/black-forest-labs/flux-2-klein-4b`, all iterations) | 40 (40 ok) | 296.12 s | 0 | $0.00 (~$0.0014/img list on CF, ~$0.015 on BFL) |
| shots (`ffmpeg-kenburns`, all iterations) | 82 (82 ok) | 680.47 s | 0 (local) | $0.00 |
| wan (`Wan 2.2 TI2V-5B`, Kaggle) | TBD | TBD | TBD | TBD (~$0.05/5s 480p, ~$0.10/5s 720p WaveSpeed ref) |
| music (`ACE-Step 1.5`, Kaggle) | TBD | TBD | TBD | TBD (~$0.027/90s WaveSpeed ref) |
| assemble (`ffmpeg`: `radio` + `film`, all iterations) | 12 (12 ok) | 835.62 s | 0 (local) | $0.00 |
