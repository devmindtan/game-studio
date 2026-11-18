"""Unit tests of soundkit (gamekit audio test)."""

import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import soundkit as sk  # noqa: E402


class SoundkitTest(unittest.TestCase):
    def test_note_freq(self):
        self.assertAlmostEqual(sk.note_freq("A4"), 440.0, places=3)
        self.assertAlmostEqual(sk.note_freq("A3"), 220.0, places=3)
        self.assertAlmostEqual(sk.note_freq("C#4"), sk.note_freq("Db4"), places=6)
        self.assertAlmostEqual(sk.note_freq("A4", octave_shift=-1), 220.0, places=3)
        with self.assertRaises(sk.AudioError):
            sk.note_freq("H4")

    def test_sfx_is_deterministic_and_normalized(self):
        spec = {"wave": "noise", "freq": 3000, "decay": 0.2, "volume": 0.6, "seed": 3}
        a, b = sk.render_sfx(spec), sk.render_sfx(spec)
        self.assertEqual(a, b)
        self.assertAlmostEqual(max(abs(v) for v in a), 0.6, places=6)

    def test_length_follows_envelope_and_delay(self):
        s = sk.render_sfx({"layers": [{"attack": 0.0, "sustain": 0.1, "decay": 0.1},
                                      {"delay": 0.3, "attack": 0.0, "sustain": 0.05, "decay": 0.05}]})
        self.assertAlmostEqual(len(s) / sk.RATE, 0.4, delta=0.01)

    def test_check_refuses_clipping_silence_and_long_sfx(self):
        with self.assertRaises(sk.AudioError):
            sk.check("sfx", "x", [0.0, 1.0])
        with self.assertRaises(sk.AudioError):
            sk.check("sfx", "x", [0.0, 0.01])
        with self.assertRaises(sk.AudioError):
            sk.check("sfx", "x", [0.5] * int(sk.RATE * 3))
        self.assertEqual(sk.check("music", "x", [0.5] * int(sk.RATE * 3))["seconds"], 3.0)

    def test_song_length_is_steps_times_step(self):
        song = {"bpm": 120, "steps_per_beat": 4, "tracks": [
            {"wave": "square", "pattern": "C4 - E4 . | G4 - - ."},
            {"wave": "drums", "pattern": "k . h . s . h ."}]}
        s = sk.render_song(song)
        self.assertAlmostEqual(len(s) / sk.RATE, 8 * 0.125, delta=0.002)

    def test_build_writes_wavs_and_removes_stale(self):
        with tempfile.TemporaryDirectory() as d:
            g = Path(d)
            src = g / "assets/source/audio"
            src.mkdir(parents=True)
            (src / "sfx.json").write_text(json.dumps({"_note": "x", "blip": {"freq": 880, "decay": 0.05}}))
            stale = g / "assets/audio/sfx/old.wav"
            stale.parent.mkdir(parents=True)
            stale.write_bytes(b"")
            sk.build(g)
            with wave.open(str(g / "assets/audio/sfx/blip.wav")) as w:
                self.assertEqual((w.getnchannels(), w.getframerate(), w.getsampwidth()), (1, sk.RATE, 2))
            self.assertFalse(stale.exists())
            self.assertIsNone(sk.wav_loop(g / "assets/audio/sfx/blip.wav"))
            self.assertTrue((g / "production/audio/review.png").exists())

    def test_music_wav_carries_a_loop(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "m.wav"
            sk.write_wav(f, [0.1] * 1000, loop=True)
            self.assertEqual(sk.wav_loop(f), (0, 999))
            with wave.open(str(f)) as w:   # still a valid WAV
                self.assertEqual(w.getnframes(), 1000)

    def test_bad_spec_is_an_audio_error(self):
        with self.assertRaises(sk.AudioError):
            sk.render_sfx({"wave": "pluck"})
        with self.assertRaises(sk.AudioError):
            sk.render_sfx({"freq": 0})


if __name__ == "__main__":
    unittest.main()
