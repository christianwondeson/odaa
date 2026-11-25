# Kaggle/Colab notes (GPU stages)
Run in a notebook, save each output as it finishes (sessions time out), then copy into this repo:
- Wan 2.2 TI2V-5B image-to-video: input `outputs/keyframes/shot_XX.jpg` + the shot's `motion_prompt`; draft at 480p; save `outputs/wan/shot_XX.mp4`. Log latency and GPU minutes by hand into runs.jsonl (stage "wan").
- ACE-Step 1.5: instrumental, 3 candidates, 45-60 s, slow tempo set in metadata (not caption). Caption idea: "warm acoustic strings, soft plucked lyre-like instrument, sparse, gentle, no strong lead melody". Save the winner as `outputs/music/chosen.wav` and write why in EXPERIMENTS.md.
