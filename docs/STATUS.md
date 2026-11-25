# Status (update honestly as you go)
- [x] Schema + storyboard.json validate (offline test, stand-in validator)
- [x] shots + assemble tested on SYNTHETIC media only (tones and colour frames): per-shot cache, subtitles, ducking, loudnorm (~ -14.4 LUFS), end card, both aspects
- [x] Smoke test against real providers  (`make smoke` — `tts` 6.71 s, `image` 7.86 s)
- [ ] Afaan Oromoo TTS reviewed by a native speaker
- [ ] Amharic TTS reviewed by a native speaker (Amharic lines are an UNVERIFIED draft; 10/10 WAVs generated)
- [ ] Language comparison logged in EXPERIMENTS.md (oro vs am: intelligibility, name/place errors, listener preference)
- [ ] Radio cut + user test 1 (3+ people; WAV preview stitched, MP4 blocked on local `ffmpeg`)
- [x] Reference sheet + keyframes (`ref_girl`, `ref_odaa`, and `shot_01`–`shot_10` generated via FLUX.2 klein 4B)
- [ ] Wan 2.2 clips (Kaggle)
- [ ] ACE-Step candidates (3) + choice
- [ ] User test 2 (3+ people)
- [ ] Walkthrough, post, report
Model ids marked "CHECK" in pipeline/*.py (TTS model, FLUX model) must be confirmed against provider docs on the day.
