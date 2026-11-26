# Status (update honestly as you go)
- [x] Schema + storyboard.json validate (offline test, stand-in validator)
- [x] shots + assemble tested on SYNTHETIC media only (tones and colour frames): per-shot cache, subtitles, ducking, loudnorm (~ -14.4 LUFS), end card, both aspects
- [x] Smoke test against real providers  (`make smoke` — `tts` 6.71 s, `image` 7.86 s)
- [ ] Afaan Oromoo TTS reviewed by a native speaker (10/10 `oro` WAVs + `film_9x16_oro.mp4` / `film_16x9_oro.mp4` built, `88.8 s`)
- [ ] Amharic TTS reviewed by a native speaker (Amharic lines are an UNVERIFIED draft; 10/10 WAVs generated)
- [ ] Language comparison logged in EXPERIMENTS.md (`oro` vs `am` full cuts built; native listener ratings 1–5 pending)
- [ ] Radio cut + user test 1 (3+ people; `radio_cut_am.mp4` `84.8 s` and `radio_cut_oro.mp4` `86.3 s` built; user test pending)
- [x] Reference sheet + keyframes (v4: unified 35mm golden-ochre/emerald look; Odaa tree motif woven continuously across shots `01`, `02`, `06`, `08`, `09`, `10`)
- [x] Animated Ken Burns + cinematic film assembly (`film_9x16.mp4` & `film_16x9.mp4` `87.3 s`; `film_9x16_oro.mp4` & `film_16x9_oro.mp4` `88.8 s`; unified FFmpeg color grade, `0.65s` `xfade` + `fadeblack` dip before `shot_07`; Wan 2.2 & ACE-Step pending)
- [ ] Wan 2.2 clips (Kaggle)
- [ ] ACE-Step candidates (3) + choice
- [ ] User test 2 (3+ people)
- [ ] Walkthrough, post, report
Model ids marked "CHECK" in pipeline/*.py (TTS model, FLUX model) must be confirmed against provider docs on the day.
