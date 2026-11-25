# Accounts and credentials (all free, no card needed as of the brief; re-check limits on the day)

| # | Service | Needed for | Sign up | What you copy into `.env` |
|---|---|---|---|---|
| 1 | Google account + AI Studio | Narration (TTS), optional script help | https://aistudio.google.com/apikey -> Create API key | `GEMINI_API_KEY` |
| 2 | Cloudflare | Keyframes (Workers AI) | https://dash.cloudflare.com/sign-up | `CF_ACCOUNT_ID`, `CF_API_TOKEN` |
| 3 | Kaggle (phone-verified) | Wan 2.2 clips, ACE-Step music (GPU) | https://www.kaggle.com -> Settings -> verify phone | nothing in `.env` (runs in notebooks) |
| 4 | Hugging Face | Downloading model weights in notebooks | https://huggingface.co/join -> Settings -> Access Tokens (read) | `HF_TOKEN` (notebook only) |
| 5 | GitHub | Public repo (submission) | https://github.com/join | none; push with the GitHub login/CLI |
| 6 | Coding agent | Optional: writes stage code | Antigravity CLI or OpenCode: follow their official install page | their own login |
| 7 | Video host | Public post | YouTube / TikTok / Facebook with AI label ON | none |

## 1. Gemini key (2 minutes)
Sign in with any Google account, open AI Studio, "Get API key" -> create. Paste into `.env` as `GEMINI_API_KEY=...`.
Model: `gemini-3.8-flash-tts` (130+ languages incl. Amharic; fallback `gemini-3.8-flash-lite-tts`, 101 languages, fewer). Voice: `Kore`.
Free-tier limits change; note what you see in COSTS.md. If you hit a quota error, wait, or switch to the lite model and log it in FAILURES.md.

## 2. Cloudflare (5 minutes)
1. Sign up and verify your email. 2. In the dashboard, copy your **Account ID** (shown on the account home / Workers & Pages overview).
3. Create an API token: profile -> API Tokens -> Create Token -> use the **Workers AI** template (or custom with Workers AI read/edit). Copy it once; you cannot see it again.
4. `.env`: `CF_ACCOUNT_ID=...`, `CF_API_TOKEN=...`.
Model: `@cf/black-forest-labs/flux-2-klein-4b` (multipart input, 4 fixed steps, up to 4 reference images, seed supported).
CAUTION: it is a partner model priced per 512x512 tile. Check in the dashboard whether it draws on your free allowance. If it is billed or blocked, set `CF_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell` (no reference images, so character consistency will be harder) and write that in FAILURES.md.

## 3. Kaggle
Sign up, then Settings -> Phone verification (needed for GPU and internet in notebooks). New Notebook -> Settings -> Accelerator: GPU T4 x2, Internet: On. Save outputs as you go; sessions time out. Weekly GPU quota is shown on your profile; record it in COSTS.md.

## Check everything
```bash
cp .env.example .env     # then edit .env
make env-check           # shows which keys are set (never prints them)
make smoke               # one TTS call + one image call, logged to runs.jsonl
```
Never paste keys in chat, screenshots, or commits. `.env` is git-ignored. If a key leaks, delete it in the provider dashboard and create a new one.
