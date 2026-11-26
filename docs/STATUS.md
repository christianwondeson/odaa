# Status (update honestly as you go)
- [x] Schema + storyboard.json validate (offline test, stand-in validator)
- [x] shots + assemble tested on SYNTHETIC media only (tones and colour frames): per-shot cache, subtitles, ducking, loudnorm (~ -14.4 LUFS), end card, both aspects
- [x] Smoke test against real providers  (`make smoke` — `tts` 6.71 s, `image` 7.86 s)
- [ ] Afaan Oromoo TTS reviewed by a native speaker (`10/10` `oro` WAVs + `film_9x16_oro.mp4` / `film_16x9_oro.mp4` built, `88.74 s` — fluent Oromo audit pending)
- [x] Amharic TTS reviewed by a native speaker (`E12`, `E13`, `E15`, `E16` — `reviewed: true` in `storyboard.json`; mother's consent recorded in `ETHICS.md`)
- [ ] Language comparison logged in EXPERIMENTS.md (`oro` vs `am` full cuts built; fluent `oro` listener audit pending)
- [x] Radio cut + user test 1 (`3/3` testers logged in `DESIGN.md`; updated audience narrowing + Shots `07`, `08`, `10` -> `radio_cut_am.mp4` `86.12 s`, `radio_cut_oro.mp4` `86.74 s`)
- [x] Reference sheet + keyframes (v4: unified 35mm golden-ochre/emerald look; Odaa tree motif woven continuously across shots `01`, `02`, `06`, `08`, `09`, `10`)
- [x] Animated Ken Burns + cinematic film assembly (`film_9x16.mp4` & `film_16x9.mp4` `88.12 s`, `mobile` `11.84 MB`; `film_9x16_oro.mp4` & `film_16x9_oro.mp4` `88.74 s`, `mobile` `12.08 MB`; unified FFmpeg color grade, `0.65s` `xfade` + `fadeblack` dip before `shot_07`; Wan 2.2 & ACE-Step pending)
- [x] Option A (`E12`) & native Amharic fixes (`E13`): Hasab AI vs Addis AI vs Gemini TTS (`am` `08`/`09`, `oro` `01`/`06`) — Gemini won storytelling warmth (`main`), and Shots `03`/`05`/`10` (`0:19`, `0:33`, `1:18` `ጥላ`) regenerated cleanly
- [ ] Wan 2.2 clips (Kaggle)
- [ ] ACE-Step candidates (3) + choice
- [ ] User test 2 (3+ people)
- [x] Walkthrough, post, report (`REPORT.md` + `REPORT.pdf` generated; Loom walkthrough `https://www.loom.com/share/74fdf0861cd84ae39ee8b21a953050e6`; TikTok post `https://www.tiktok.com/@christianwondeson/video/7712532010245360902`)
Model ids marked "CHECK" in pipeline/*.py (TTS model, FLUX model) must be confirmed against provider docs on the day.
