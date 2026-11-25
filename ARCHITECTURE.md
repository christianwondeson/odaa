# ARCHITECTURE
Contract: `storyboard.json`, validated against `schema/storyboard.schema.json` at the start of EVERY stage (`load_storyboard`).
Stages are independent scripts; each reads the contract and writes `outputs/<stage>/`.
Caching: key = stage+shot(+aspect); value = sha256 of the inputs (prompt, seed, model, camera, duration, source file hash). Skip if hash matches and the file exists.
Timing: narration length sets shot length (`shot_seconds`), so changing a narration line re-renders only that shot's clip, and assembly recomputes the track.
Failure handling: `retry` with exponential backoff (3 tries); errors are logged to runs.jsonl with status=error; missing Wan clip falls back to Ken Burns; missing score falls back to a placeholder pad (flagged in the log).
Logging: one JSON line per model call: ts, stage, model, shot, params, seed, latency_s, cost_usd, status.
Secrets: `.env` only, git-ignored.
