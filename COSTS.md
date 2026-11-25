# COSTS
Measure from runs.jsonl: latency per stage, GPU minutes (Kaggle), free-tier limits as found today, list-price equivalent.
| Stage | Calls | Total latency | GPU min | List-price equiv. |
|---|---|---|---|---|
| smoke_tts (`gemini-3.8-flash-tts`) | 1 (1 ok) | 6.71 s | 0 | $0.00 (AI Studio free tier) |
| smoke_image (`@cf/black-forest-labs/flux-2-klein-4b`) | 1 (1 ok) | 7.86 s | 0 | $0.00 (Cloudflare free tier) |
| narration (`am`, `gemini-3.8-flash-tts`) | 11 (10 ok, 1 `429`) | 67.61 s | 0 | $0.00 (AI Studio free tier; ~9 RPM hit) |
| keyframes (`ref_girl`, `ref_odaa`, `shot_01`–`shot_10`) | 12 (12 ok) | 89.30 s | 0 | $0.00 (Cloudflare free allowance; verify tile billing) |
| wan (`Wan 2.2 TI2V-5B`, Kaggle) | TBD | TBD | TBD | TBD |
| music (`ACE-Step 1.5`, Kaggle) | TBD | TBD | TBD | TBD |
| assemble (`ffmpeg`) | TBD | TBD | 0 (local) | $0.00 |
