# Status (update honestly as you go)
- [x] Schema + storyboard.json validate (offline test, stand-in validator)
- [x] shots + assemble tested on SYNTHETIC media only (tones and colour frames): per-shot cache, subtitles, ducking, loudnorm (~ -14.4 LUFS), end card, both aspects
- [x] Smoke test against real providers  (`make smoke` — `tts` 6.71 s, `image` 7.86 s)
- [ ] Afaan Oromoo TTS reviewed by a native speaker
- [ ] Amharic TTS reviewed by a native speaker (Amharic lines are an UNVERIFIED draft; 10/10 WAVs generated)
- [ ] Language comparison logged in EXPERIMENTS.md (oro vs am: intelligibility, name/place errors, listener preference)
- [ ] Radio cut + user test 1 (3+ people; `outputs/final/radio_cut_am.mp4` rebuilt — 84.8 s, bilingual title & subtitles; user test pending)
- [x] Reference sheet + keyframes (v4 on `ceiling/oromo-and-benchmark`: unified 35mm golden-ochre/emerald look; Odaa tree motif woven continuously across shots `01`, `02`, `06`, `08`, `09`, `10`)
- [x] Animated Ken Burns + cinematic film assembly (`film_9x16.mp4` and `film_16x9.mp4`, 87.3 s incl. 2.5s end card, unified FFmpeg color grade, `0.65s` `xfade` + `fadeblack` dip before `shot_07`, bilingual Amharic+English title/subs; Wan 2.2 & ACE-Step pending)
- [ ] Wan 2.2 clips (Kaggle)
- [ ] ACE-Step candidates (3) + choice
- [ ] User test 2 (3+ people)
- [ ] Walkthrough, post, report
Model ids marked "CHECK" in pipeline/*.py (TTS model, FLUX model) must be confirmed against provider docs on the day.
