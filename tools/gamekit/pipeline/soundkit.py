"""Procedural game audio for game-studio: sfxr-style effects and a tiny tracker.

Pure Python (stdlib + Pillow for the review sheet). Everything is deterministic:
the same JSON gives the same .wav, so sounds are source code like sprite gen.py.

    python3 soundkit.py <game_dir> [--only id[,id]] [--play id]

Sources (in the game):
    assets/source/audio/sfx.json    {"<id>": layer | {"layers": [layer, ...]}, ...}
    assets/source/audio/music.json  {"<id>": song, ...}
Output:
    assets/audio/sfx/<id>.wav, assets/audio/music/<id>.wav (mono, 16-bit, 22050 Hz)
    production/audio/review.png (waveform per sound) + review.txt (length, peak, rms)

A layer (all keys optional):
    wave      square | saw | triangle | sine | noise     (default square)
    freq      start pitch, Hz (default 440)
    freq_end  end pitch, Hz: exponential slide over the layer (default = freq)
    duty      square duty 0..1 (default 0.5)
    attack, sustain, decay   envelope seconds (defaults 0.005, 0.05, 0.15)
    punch     extra level at the start of sustain, 0..1
    vibrato   [depth 0..1, speed Hz]
    arp       [[time_s, freq_multiplier], ...] pitch jumps (coin / power-up)
    lowpass, highpass        one-pole filter cutoffs, Hz
    delay     start time inside the sound, s
    gain      layer mix level (default 1)
    seed      noise seed (default 1)
A sound may also set "volume" (peak after mixing, default 0.8).

A song: {"bpm": 120, "steps_per_beat": 4, "volume": 0.7, "repeat": 1,
         "tracks": [{"wave": "square", "duty": 0.25, "gain": 0.3, "octave": 0,
                     "attack": .005, "decay": .12, "sustain_level": .5, "release": .05,
                     "pattern": "C4 - E4 . G4 - . . | ...", "times": 1}, ...]}
Pattern tokens, one per step: a note (C4, D#3, Bb2), "-" hold the previous note,
"." rest, "|" ignored (bar line). Drum tracks ("wave": "drums") use k (kick),
s (snare), h (hat), "." rest. A track's pattern loops until the song ends; the
song length is the longest pattern x "times".
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import subprocess
import sys
import wave
from array import array
from pathlib import Path

RATE = 22050
MAX_SFX_S = 2.5          # an effect longer than this is a mistake (music goes in music.json)
PEAK_LIMIT = 0.98        # refuse clipping
MIN_PEAK = 0.05          # refuse silence


class AudioError(Exception):
    pass


# ---------------------------------------------------------------- oscillators

def _osc(wave_name, phase, duty, rng):
    p = phase % 1.0
    if wave_name == "square":
        return 1.0 if p < duty else -1.0
    if wave_name == "saw":
        return 2.0 * p - 1.0
    if wave_name == "triangle":
        return 4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p
    if wave_name == "sine":
        return math.sin(2.0 * math.pi * p)
    if wave_name == "noise":
        return rng.uniform(-1.0, 1.0)
    raise AudioError(f"unknown wave {wave_name!r}")


class _OnePole:
    """One-pole low/high pass; cutoff None = pass-through."""

    def __init__(self, lowpass=None, highpass=None):
        self.lp = None if not lowpass else 1.0 - math.exp(-2.0 * math.pi * lowpass / RATE)
        self.hp = None if not highpass else math.exp(-2.0 * math.pi * highpass / RATE)
        self._l = 0.0
        self._hx = 0.0
        self._hy = 0.0

    def __call__(self, x):
        if self.lp is not None:
            self._l += self.lp * (x - self._l)
            x = self._l
        if self.hp is not None:
            y = self.hp * (self._hy + x - self._hx)
            self._hx, self._hy = x, y
            x = y
        return x


# ---------------------------------------------------------------- effects

def render_layer(layer):
    """Samples (floats -1..1) of one sfxr-style layer, starting at its delay."""
    wave_name = layer.get("wave", "square")
    f0 = float(layer.get("freq", 440.0))
    f1 = float(layer.get("freq_end", f0))
    duty = float(layer.get("duty", 0.5))
    att = float(layer.get("attack", 0.005))
    sus = float(layer.get("sustain", 0.05))
    dec = float(layer.get("decay", 0.15))
    punch = float(layer.get("punch", 0.0))
    vib = layer.get("vibrato") or [0.0, 0.0]
    arp = sorted(layer.get("arp") or [])
    gain = float(layer.get("gain", 1.0))
    rng = random.Random(layer.get("seed", 1))
    filt = _OnePole(layer.get("lowpass"), layer.get("highpass"))
    if f0 <= 0 or f1 <= 0:
        raise AudioError("freq and freq_end must be > 0")
    total = att + sus + dec
    n = max(1, int(total * RATE))
    out = [0.0] * (int(float(layer.get("delay", 0.0)) * RATE))
    phase = 0.0
    noise_val = 0.0
    noise_phase = 0.0
    for i in range(n):
        t = i / RATE
        k = i / n
        freq = f0 * (f1 / f0) ** k
        for at, mul in arp:      # each passed jump multiplies the pitch (cumulative, like sfxr)
            if t >= at:
                freq *= mul
        if vib[0]:
            freq *= 1.0 + vib[0] * math.sin(2.0 * math.pi * vib[1] * t)
        if t < att:
            env = t / att if att > 0 else 1.0
        elif t < att + sus:
            env = 1.0 + punch * (1.0 - (t - att) / sus if sus > 0 else 0.0)
        else:
            env = max(0.0, 1.0 - (t - att - sus) / dec) if dec > 0 else 0.0
        if wave_name == "noise":
            # sample-and-hold noise: freq sets the grain (low = rumble, high = hiss)
            noise_phase += freq / RATE
            if noise_phase >= 1.0 or i == 0:
                noise_phase %= 1.0
                noise_val = rng.uniform(-1.0, 1.0)
            s = noise_val
        else:
            phase += freq / RATE
            s = _osc(wave_name, phase, duty, rng)
        out.append(filt(s) * env * gain)
    return out


def mix(parts):
    n = max((len(p) for p in parts), default=0)
    out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p):
            out[i] += v
    return out


def normalize(samples, peak):
    top = max((abs(v) for v in samples), default=0.0)
    if top <= 0:
        raise AudioError("silent")
    k = peak / top
    return [v * k for v in samples]


def render_sfx(spec):
    layers = spec.get("layers") or [spec]
    samples = mix([render_layer(layer) for layer in layers])
    # 3 ms fade-out so a cut never clicks
    fade = min(len(samples), int(0.003 * RATE))
    for j in range(fade):
        samples[-1 - j] *= j / fade
    return normalize(samples, float(spec.get("volume", 0.8)))


# ---------------------------------------------------------------- music

_NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_freq(token, octave_shift=0):
    """'A4' -> 440.0; accepts sharps (C#4) and flats (Bb3)."""
    name = token[0].upper()
    if name not in _NOTE:
        raise AudioError(f"bad note {token!r}")
    rest = token[1:]
    semi = _NOTE[name]
    while rest and rest[0] in "#b":
        semi += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    try:
        octave = int(rest) + octave_shift
    except ValueError:
        raise AudioError(f"bad note {token!r}") from None
    midi = 12 * (octave + 1) + semi
    return 440.0 * 2 ** ((midi - 69) / 12)


def _tokens(pattern):
    return [t for t in pattern.split() if t != "|"]


def _drum(kind, rng):
    if kind == "k":
        return render_layer({"wave": "sine", "freq": 150, "freq_end": 45, "attack": 0.001,
                             "sustain": 0.02, "decay": 0.16, "punch": 0.5, "gain": 1.0})
    if kind == "s":
        return mix([render_layer({"wave": "noise", "freq": 6000, "attack": 0.001, "sustain": 0.01,
                                  "decay": 0.12, "highpass": 900, "gain": 0.7, "seed": rng.random()}),
                    render_layer({"wave": "triangle", "freq": 220, "freq_end": 160, "attack": 0.001,
                                  "sustain": 0.0, "decay": 0.06, "gain": 0.4})])
    if kind == "h":
        return render_layer({"wave": "noise", "freq": 11000, "attack": 0.0005, "sustain": 0.0,
                             "decay": 0.035, "highpass": 5000, "gain": 0.35, "seed": rng.random()})
    raise AudioError(f"bad drum {kind!r} (k, s, h, .)")


def render_song(song):
    bpm = float(song.get("bpm", 120))
    spb = int(song.get("steps_per_beat", 4))
    step = 60.0 / bpm / spb
    tracks = song.get("tracks") or []
    if not tracks:
        raise AudioError("song has no tracks")
    steps = max(len(_tokens(t["pattern"])) * int(t.get("times", 1)) for t in tracks)
    steps *= int(song.get("repeat", 1))
    n = int(steps * step * RATE)
    out = [0.0] * n
    for t in tracks:
        toks = _tokens(t["pattern"])
        if not toks:
            continue
        gain = float(t.get("gain", 0.3))
        rng = random.Random(t.get("seed", 7))
        if t.get("wave") == "drums":
            for s in range(steps):
                tok = toks[s % len(toks)]
                if tok in (".", "-"):
                    continue
                hit = _drum(tok, rng)
                start = int(s * step * RATE)
                for i, v in enumerate(hit):
                    if start + i < n:
                        out[start + i] += v * gain
            continue
        # melodic: gather notes with their lengths in steps
        notes = []
        for s in range(steps):
            tok = toks[s % len(toks)]
            if tok == "-":
                if notes and notes[-1][2]:
                    notes[-1][1] += 1
                continue
            if tok == ".":
                notes.append([s, 1, None])
                continue
            notes.append([s, 1, note_freq(tok, int(t.get("octave", 0)))])
        layer = {k: t[k] for k in ("wave", "duty", "lowpass", "highpass", "vibrato") if k in t}
        att = float(t.get("attack", 0.005))
        dec = float(t.get("decay", 0.1))
        lvl = float(t.get("sustain_level", 0.6))
        rel = float(t.get("release", 0.05))
        for start_step, length, freq in notes:
            if freq is None:
                continue
            dur = length * step
            m = int((dur + rel) * RATE)
            phase = 0.0
            filt = _OnePole(t.get("lowpass"), t.get("highpass"))
            vib = layer.get("vibrato") or [0.0, 0.0]
            start = int(start_step * step * RATE)
            for i in range(m):
                tt = i / RATE
                if tt < att:
                    env = tt / att
                elif tt < att + dec:
                    env = 1.0 - (1.0 - lvl) * (tt - att) / dec
                elif tt < dur:
                    env = lvl
                else:
                    env = lvl * max(0.0, 1.0 - (tt - dur) / rel)
                f = freq * (1.0 + vib[0] * math.sin(2.0 * math.pi * vib[1] * tt)) if vib[0] else freq
                phase += f / RATE
                v = filt(_osc(layer.get("wave", "square"), phase, float(layer.get("duty", 0.5)), rng))
                j = (start + i) % n   # the release of the last note wraps to the loop start
                out[j] += v * env * gain
    return normalize(out, float(song.get("volume", 0.7)))


# ---------------------------------------------------------------- files

def write_wav(path, samples, loop=False):
    """16-bit mono WAV. loop=True adds a "smpl" chunk (forward loop over the whole
    file), which Godot's WAV importer reads as the loop (import "Detect From WAV")."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = array("h", (int(max(-1.0, min(1.0, v)) * 32767) for v in samples))
    if sys.byteorder == "big":
        data.byteswap()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())
    if loop:
        smpl = struct.pack("<9I", 0, 0, 1_000_000_000 // RATE, 60, 0, 0, 0, 1, 0)
        smpl += struct.pack("<6I", 0, 0, 0, max(0, len(samples) - 1), 0, 0)
        raw = bytearray(path.read_bytes())
        raw += b"smpl" + struct.pack("<I", len(smpl)) + smpl
        raw[4:8] = struct.pack("<I", len(raw) - 8)
        path.write_bytes(bytes(raw))


def wav_loop(path):
    """(start, end) of the first smpl loop in a WAV, or None."""
    raw = Path(path).read_bytes()
    i = 12
    while i + 8 <= len(raw):
        cid, size = raw[i:i + 4], struct.unpack("<I", raw[i + 4:i + 8])[0]
        if cid == b"smpl" and size >= 60:
            return struct.unpack("<2I", raw[i + 8 + 44:i + 8 + 52])
        i += 8 + size + (size & 1)
    return None


def stats(samples):
    peak = max((abs(v) for v in samples), default=0.0)
    rms = math.sqrt(sum(v * v for v in samples) / max(1, len(samples)))
    return {"seconds": round(len(samples) / RATE, 3), "peak": round(peak, 3), "rms": round(rms, 3)}


def check(kind, sid, samples):
    st = stats(samples)
    if st["peak"] > PEAK_LIMIT:
        raise AudioError(f"{kind} {sid}: clipping (peak {st['peak']})")
    if st["peak"] < MIN_PEAK:
        raise AudioError(f"{kind} {sid}: nearly silent (peak {st['peak']})")
    if kind == "sfx" and st["seconds"] > MAX_SFX_S:
        raise AudioError(f"sfx {sid}: {st['seconds']}s is too long for an effect (max {MAX_SFX_S}s)")
    return st


def review_sheet(path, rows):
    """One waveform strip per sound: min/max per pixel column, labelled."""
    from PIL import Image, ImageDraw
    w, h, pad = 520, 44, 4
    img = Image.new("RGB", (w + 180, max(1, len(rows)) * (h + pad) + pad), (24, 24, 30))
    d = ImageDraw.Draw(img)
    for r, (label, samples, st) in enumerate(rows):
        y0 = pad + r * (h + pad)
        d.rectangle([180, y0, 180 + w - 1, y0 + h - 1], fill=(36, 36, 46))
        d.line([180, y0 + h // 2, 180 + w - 1, y0 + h // 2], fill=(60, 60, 74))
        n = len(samples)
        cols = min(w, n)
        for c in range(cols):
            a = samples[c * n // cols:(c + 1) * n // cols] or [0.0]
            lo, hi = min(a), max(a)
            d.line([180 + c, y0 + h // 2 - int(hi * h / 2), 180 + c, y0 + h // 2 - int(lo * h / 2)],
                   fill=(120, 200, 255))
        d.text((6, y0 + 4), label, fill=(230, 230, 230))
        d.text((6, y0 + 22), f"{st['seconds']}s pk {st['peak']} rms {st['rms']}", fill=(150, 150, 160))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def load(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise AudioError(f"{path}: {e}") from None
    return {k: v for k, v in data.items() if not k.startswith("_")}


def build(game, only=None):
    src = game / "assets" / "source" / "audio"
    sfx, music = load(src / "sfx.json"), load(src / "music.json")
    if not sfx and not music:
        raise AudioError(f"nothing to build: add {src}/sfx.json or music.json")
    rows, lines = [], []
    for kind, defs, render, sub in (("sfx", sfx, render_sfx, "sfx"), ("music", music, render_song, "music")):
        for sid, spec in defs.items():
            if only and sid not in only:
                continue
            try:
                samples = render(spec)
            except (KeyError, TypeError, ValueError) as e:
                raise AudioError(f"{kind} {sid}: bad spec ({e})") from None
            st = check(kind, sid, samples)
            write_wav(game / "assets" / "audio" / sub / f"{sid}.wav", samples, loop=kind == "music")
            rows.append((f"{kind}/{sid}", samples, st))
            lines.append(f"{kind}/{sid}\t{st['seconds']}s\tpeak {st['peak']}\trms {st['rms']}")
    if not only:
        # drop wavs whose source entry is gone
        for kind, defs in (("sfx", sfx), ("music", music)):
            for f in (game / "assets" / "audio" / kind).glob("*.wav"):
                if f.stem not in defs:
                    f.unlink()
                    imp = f.with_name(f.name + ".import")
                    if imp.exists():
                        imp.unlink()
                    lines.append(f"removed {kind}/{f.name}")
        review_sheet(game / "production" / "audio" / "review.png", rows)
        (game / "production" / "audio" / "review.txt").write_text("\n".join(lines) + "\n")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("game")
    ap.add_argument("--only", default="", help="comma-separated ids to rebuild")
    ap.add_argument("--play", default="", help="build then play this id (pw-play/paplay/aplay)")
    a = ap.parse_args(argv)
    game = Path(a.game).resolve()
    only = set(filter(None, a.only.split(","))) or None
    try:
        lines = build(game, only)
    except AudioError as e:
        print(f"soundkit: {e}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    if a.play:
        for sub in ("sfx", "music"):
            f = game / "assets" / "audio" / sub / f"{a.play}.wav"
            if f.exists():
                for player in ("pw-play", "paplay", "aplay"):
                    try:
                        subprocess.run([player, str(f)], check=False)
                        break
                    except FileNotFoundError:
                        continue
                break
        else:
            print(f"soundkit: no sound {a.play!r}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["render_layer", "render_sfx", "render_song", "note_freq", "write_wav", "wav_loop", "stats", "check",
           "build", "AudioError", "RATE"]
