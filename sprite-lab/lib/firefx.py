"""firefx: fire effects at double pixel density (fireball blast, meteor), like icefx.

Each has readable phases (user 2026-11-18: effects must not pop in and out):
  blast:  flash -> fireball swells -> smoke and embers linger -> fade (dither)
  meteor: a warning mark -> the rock falls with a trail -> crater burst ->
          the ground smoulders -> fade
Frames are twice the old size; gen.py writes "px_scale": 0.5. Tiers add rings,
more embers, a shock ring (4+) and a molten core (5).
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
from icefx import BAYER, _disk, _fade, _p, _ring

WHITE = "#fff8e0"
YEL = "#ffd84a"
ORA = "#ff8a2a"
RED = "#e0402a"
DRED = "#8a1f1f"
SMOKE = "#5a4a50"
SMOKE_L = "#8a7a80"
ASH = "#3a2e34"
ROCK = "#4a3a3a"
ROCK_L = "#7a5a4a"


def _blob(c, cx, cy, r, col, density=1.0, wobble=0.0, seed=0):
    """A rough round flame mass (radius jitters with the angle)."""
    rng = random.Random(seed)
    bumps = [rng.uniform(-wobble, wobble) for _ in range(12)]
    ri = int(math.ceil(r + wobble + 1))
    for y in range(-ri, ri + 1):
        for x in range(-ri, ri + 1):
            a = math.atan2(y, x)
            k = (a + math.pi) / math.tau * 12
            i0 = int(k) % 12
            rr = r + bumps[i0] + (bumps[(i0 + 1) % 12] - bumps[i0]) * (k - int(k))
            if x * x + y * y <= rr * rr:
                px, py = int(cx + x), int(cy + y)
                if BAYER[py % 4][px % 4] < density * 16:
                    _p(c, px, py, col)


BLAST_MS = [50, 60, 60, 70, 70, 90, 100, 110, 110, 120]


def blast(tier, size, radius, seed=3):
    """10 frames: a fireball blast centred in a size x size frame."""
    cx = cy = size / 2
    rng = random.Random(seed)
    embers = [(rng.uniform(0, math.tau), rng.uniform(0.4, 1.0), rng.uniform(0.6, 1.4)) for _ in range(10 + 4 * tier)]
    out = []
    for f in range(10):
        c = Canvas(size, size)
        if f == 0:   # flash
            _disk(c, cx, cy, radius * 0.35, YEL)
            _disk(c, cx, cy, radius * 0.22, WHITE)
        elif f <= 4:   # swell
            t = f / 4
            r = radius * (0.45 + 0.55 * t)
            _blob(c, cx, cy, r, DRED, wobble=2 + tier * 0.4, seed=f)
            _blob(c, cx, cy, r * 0.85, RED, wobble=2, seed=f + 9)
            _blob(c, cx, cy, r * 0.62, ORA, wobble=1.5, seed=f + 17)
            _blob(c, cx, cy, r * 0.38 * (1.2 - t * 0.5), YEL, wobble=1, seed=f + 23)
            _disk(c, cx, cy, max(1, r * 0.16 * (1.3 - t)), WHITE)
            if tier >= 4:
                _ring(c, cx, cy, r + 3 + f, ORA)
            if tier >= 5:
                _ring(c, cx, cy, r * 0.5, WHITE)
        else:          # smoke and embers, then fade
            k = f - 4
            r = radius * (0.9 + 0.05 * k)
            _blob(c, cx, cy - k, r * (0.8 - 0.05 * k), SMOKE, density=0.55 - 0.05 * k, wobble=3, seed=40 + k)
            _blob(c, cx, cy - k, r * (0.55 - 0.05 * k), SMOKE_L, density=0.35, wobble=2, seed=50 + k)
            _blob(c, cx, cy, max(1, r * (0.35 - 0.06 * k)), ORA, wobble=1.5, seed=60 + k)
            for a, d, s in embers:
                rr = radius * d * (1 + 0.12 * k)
                _p(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr - k * s * 2, YEL if (k + int(a * 3)) % 2 else ORA)
            if f >= 7:
                _fade(c, min(0.95, 0.15 + 0.25 * (f - 6)))
        out.append(c)
    return out


METEOR_MS = [90, 90, 60, 50, 50, 60, 70, 80, 110, 120, 120, 130, 140]


def meteor(tier, w, h, ground, radius, seed=5):
    """13 frames: mark, fall, impact, smoulder, fade. ground = the impact point's y;
    the rock falls from the top-right."""
    cx, cy = w / 2, ground
    rng = random.Random(seed)
    rocks = [(rng.uniform(0, math.tau), rng.uniform(0.3, 1.0)) for _ in range(8 + 2 * tier)]
    rr = 5 + tier
    out = []
    for f in range(13):
        c = Canvas(w, h)
        if f < 5:   # warning mark grows; the rock falls in on frames 2..4
            mark = radius * (0.5 + 0.12 * f)
            _ring(c, cx, cy, mark, RED if f % 2 else DRED)
            if f >= 2:
                t = (f - 1) / 4
                mx, my = cx + (1 - t) * w * 0.35, cy - (1 - t) * (h - 6) + rr
                for k in range(1, 7):   # trail
                    _disk(c, mx + k * 3, my - k * 5, max(1, rr - k), [YEL, ORA, ORA, RED, RED, DRED][k - 1])
                _disk(c, mx, my, rr, ROCK)
                _disk(c, mx - 1, my - 1, rr * 0.6, ROCK_L)
                _p(c, mx - rr * 0.5, my - rr * 0.5, YEL)
        elif f < 8:   # impact
            t = (f - 4) / 3
            r = radius * (0.5 + 0.5 * t)
            _blob(c, cx, cy, r, DRED, wobble=3, seed=f)
            _blob(c, cx, cy, r * 0.8, RED, wobble=2, seed=f + 3)
            _blob(c, cx, cy, r * 0.55, ORA, wobble=2, seed=f + 5)
            _blob(c, cx, cy, r * 0.3, YEL, wobble=1, seed=f + 7)
            if f == 5:
                _disk(c, cx, cy, r * 0.18, WHITE)
            for a, d in rocks:   # debris flies out
                _p(c, cx + math.cos(a) * r * (0.9 + d * t), cy + math.sin(a) * r * (0.9 + d * t) - 3 * t, ROCK_L)
            if tier >= 4:
                _ring(c, cx, cy, r + 2, YEL)
        else:         # crater smoulders, then fades
            k = f - 8
            _disk(c, cx, cy, radius * 0.7, ASH, density=0.6)
            _ring(c, cx, cy, radius * 0.7, ROCK)
            _blob(c, cx, cy, radius * 0.35, RED, density=0.6 - 0.08 * k, wobble=2, seed=70 + k)
            _blob(c, cx, cy, radius * 0.2, ORA, density=0.7, wobble=1, seed=80 + k)
            if tier >= 5:
                _disk(c, cx, cy, 3, YEL)
            for a, d in rocks:
                _p(c, cx + math.cos(a) * radius * d * 0.8, cy + math.sin(a) * radius * d * 0.8 - k * 2, SMOKE_L)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.2 * k))
        out.append(c)
    return out
