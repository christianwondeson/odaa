# COSTS
Measure from runs.jsonl: latency per stage, GPU minutes (Kaggle), free-tier limits as found today, list-price equivalent.
| Stage | Calls | Total latency | GPU min | List-price equiv. |
|---|---|---|---|---|
| smoke_tts (`gemini-3.8-flash-tts`) | 1 (1 ok) | 6.71 s | 0 | $0.00 (AI Studio free tier) |
| smoke_image (`@cf/black-forest-labs/flux-2-klein-4b`) | 1 (1 ok) | 7.86 s | 0 | $0.00 (Cloudflare free tier) |
| narration (`am` + `oro`, `gemini-3.8-flash-tts`) | 32 (25 ok, 7 err) | 507.13 s | 0 | $0.00 (10 RPD cap; ~$0.002/10s list) |
| narration (`am` + `oro`, `gemini-3.8-flash-lite-tts`) | 16 (16 ok) | 171.24 s | 0 | $0.00 (10 RPD cap; ~$0.0015/10s list) |
| narration (`am` + `oro` test, `gemini-2.5-flash-preview-tts`) | 5 (5 ok) | 65.08 s | 0 | $0.00 (AI Studio free tier) |
| benchmark_tts (`hasab:Selam` + `hasab:Lemlem`) | 8 (8 ok) | 35.98 s | 0 | Evaluation tier (~4.5s/shot) |
| benchmark_tts (`addis:am-hamen` + `addis:om-ayyaantuu`) | 6 (4 ok, 2 err) | 18.48 s | 0 | $0.00 (signup trial credit; ~$0.031/voice min list) |
| benchmark_tts (`gemini-3.8-flash` + `lite`) | 6 (6 ok) | 77.55 s | 0 | $0.00 (AI Studio free tier) |
| keyframes (`@cf/black-forest-labs/flux-2-klein-4b`, all iterations) | 52 (52 ok) | 500.58 s | 0 | $0.00 (~$0.0014/img list on CF, ~$0.015 on BFL) |
| benchmark_image (`@cf/black-forest-labs/flux-1-schnell`) | 2 (2 ok) | 64.30 s | 0 | $0.00 (Cloudflare free tier) |
| shots (`ffmpeg-kenburns`, all iterations) | 208 (208 ok) | 2258.75 s | 0 (local) | $0.00 |
| wan (`Wan 2.2 TI2V-5B`, Kaggle) | TBD | TBD | TBD | TBD (~$0.05/5s 480p, ~$0.10/5s 720p WaveSpeed ref) |
| music (`ACE-Step 1.5`, Kaggle) | TBD | TBD | TBD | TBD (~$0.027/90s WaveSpeed ref) |
| assemble (`ffmpeg`: `radio` + `film`, `am` + `oro`) | 26 (26 ok) | 2239.57 s | 0 (local) | $0.00 |
