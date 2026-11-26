"""Offline unit tests for storyboard contract, caching, voice overrides, TTS provider adapters, and ASS/FFmpeg helpers."""
import json, pathlib, tempfile, unittest
from unittest.mock import MagicMock, patch

from pipeline import assemble, common, narration, providers


def _sine_mp3_bytes():
    """Create tiny valid MP3 bytes via ffmpeg so _to_wav conversion is tested end-to-end."""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        mp3 = pathlib.Path(td) / "s.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=440:d=0.25", str(mp3)],
            check=True,
        )
        return mp3.read_bytes()


class PipelineTests(unittest.TestCase):
    def test_storyboard_schema_valid(self):
        sb = common.load_storyboard()
        self.assertEqual(len(sb["shots"]), 10)
        self.assertIn("am", sb["narration"]["languages"])
        self.assertIn("oro", sb["narration"]["languages"])
        for s in sb["shots"]:
            self.assertTrue(s["reason"])
            self.assertTrue(s["narration"]["am"])
            self.assertTrue(s["narration"]["oro"])

    def test_voice_override_scoped_by_language(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td)
            (out / "voice_override" / "am").mkdir(parents=True)
            (out / "voice_override" / "am" / "shot_08.wav").write_bytes(b"RIFFtest")
            (out / "narration" / "oro").mkdir(parents=True)
            (out / "narration" / "oro" / "shot_08.wav").write_bytes(b"RIFForo")
            with patch.object(common, "OUT", out):
                with patch.dict("os.environ", {"NARRATION_LANG": "am"}):
                    self.assertEqual(common.narration_audio_path("08"), out / "voice_override" / "am" / "shot_08.wav")
                    self.assertEqual(common.narration_tempo("08"), 1.0)
                with patch.dict("os.environ", {"NARRATION_LANG": "oro"}):
                    self.assertEqual(common.narration_audio_path("08"), out / "narration" / "oro" / "shot_08.wav")
                    self.assertAlmostEqual(common.narration_tempo("08"), 1.22)
                with patch.dict("os.environ", {"NARRATION_LANG": "oro", "TTS_PROVIDER": "addis"}):
                    self.assertEqual(common.narration_tempo("08"), 1.0)

    def test_ff_path_and_bilingual_cues(self):
        escaped = assemble.ff_path(pathlib.Path("outputs/work/test.ass"))
        self.assertTrue(escaped.startswith("'") and escaped.endswith("'"))
        self.assertIn(r"\:", escaped)
        sb = common.load_storyboard()
        with patch.dict("os.environ", {"NARRATION_LANG": "oro"}):
            cues = assemble.build_bilingual_cues(sb, [float(s["min_seconds"]) for s in sb["shots"]], 40)
        self.assertEqual(len(cues), 10)
        self.assertIn("Odaa", cues[0][2])

    def test_hasab_and_addis_tts_adapters(self):
        fake_wav = providers._pcm_to_wav(b"\x00\x00" * 1200)
        mp3_bytes = _sine_mp3_bytes()

        with patch.dict("os.environ", {"HASAB_API_KEY": "hk_test", "ADDIS_API_KEY": "ak_test"}):
            with patch("pipeline.providers.requests.post") as mock_post:
                resp = MagicMock(status_code=200, content=fake_wav, headers={"content-type": "audio/wav"})
                mock_post.return_value = resp
                wav = providers.hasab_tts("ሰላም", lang="am")
                self.assertEqual(wav[:4], b"RIFF")
                _, kwargs = mock_post.call_args
                self.assertEqual(kwargs["json"]["language"], "amh")
                self.assertEqual(kwargs["json"]["speaker_name"], "Selam")

            with patch("pipeline.providers.requests.post") as mock_post:
                resp = MagicMock(ok=True, status_code=200, content=mp3_bytes, headers={"content-type": "audio/mpeg"})
                mock_post.return_value = resp
                wav = providers.addis_tts("Nagaa", lang="oro")
                self.assertEqual(wav[:4], b"RIFF")
                _, kwargs = mock_post.call_args
                self.assertEqual(kwargs["json"]["language"], "om")
                self.assertEqual(kwargs["json"]["voice_id"], "om-ayyaantuu")
                self.assertTrue(kwargs["json"]["client_request_id"])
                self.assertEqual(kwargs["headers"]["x-api-key"], "ak_test")

    def test_tts_chain_switches_on_daily_quota(self):
        import requests
        fake_wav = providers._pcm_to_wav(b"\x00\x00" * 1200)
        err_resp = MagicMock(status_code=429, text="limit: 10 requests per day on Free Tier")
        http_err = requests.HTTPError("429", response=err_resp)
        exhausted = set()

        def fake_gemini(text, style, voice, model):
            if model == "gemini-3.8-flash-tts":
                raise http_err
            return fake_wav

        with patch("pipeline.narration.gemini_tts", side_effect=fake_gemini), \
             patch("pipeline.common.time.sleep", return_value=None):
            wav, used = narration.tts_call("hi", "calm", "Kore", narration.TTS_CHAIN, exhausted)
        self.assertEqual(wav, fake_wav)
        self.assertEqual(used, "gemini-3.8-flash-lite-tts")
        self.assertIn("gemini-3.8-flash-tts", exhausted)

    def test_assemble_xfade_pads_short_clip_without_truncation(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td)
            (out / "shots" / "am").mkdir(parents=True)
            (out / "narration" / "am").mkdir(parents=True)
            clip_dir = out / "shots" / "am"
            for i, sid in enumerate(("01", "02")):
                dur_clip = 2.0 if sid == "01" else 3.0  # intentionally shorter than shot_seconds (6s/8s)
                subprocess.run(
                    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=black:s=320x180:r=24:d={dur_clip}", str(clip_dir / f"shot_{sid}_16x9.mp4")],
                    check=True,
                )
            self.assertTrue((clip_dir / "shot_01_16x9.mp4").exists())
            self.assertGreater(assemble.media_duration(clip_dir / "shot_01_16x9.mp4"), 1.5)


if __name__ == "__main__":
    unittest.main()
