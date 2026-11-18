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


BLAST_MS = [60, 50, 55, 60, 70, 80, 90, 100, 100, 110, 110, 120]


def blast(tier, size, radius, seed=3):
    """12 frames: charge, flash with rays, fireball swells, smoke and embers, fade."""
    import fxkit as fk
    cx = cy = size / 2
    radius = min(radius, size / 2 - 4)
    rng = random.Random(seed)
    embers = [(rng.uniform(0, math.tau), rng.uniform(0.5, 1.1), rng.uniform(0.6, 1.4)) for _ in range(12 + 4 * tier)]
    out = []
    for f in range(12):
        c = Canvas(size, size)
        if f == 0:   # the fireball's core flares before it bursts
            fk.glow(c, cx, cy, radius * 0.3, [RED, ORA, YEL, WHITE])
            fk.sparkle(c, int(cx), int(cy), 3 + tier, WHITE, YEL)
        elif f == 1:   # flash
            fk.glow(c, cx, cy, radius * 0.6, [ORA, YEL, WHITE], density=0.9)
            fk.rays(c, cx, cy, radius * 0.4, radius, 10 + 2 * tier, YEL, WHITE, rot=0.2, width=2)
        elif f <= 4:   # swell
            t = (f - 1) / 3
            r = radius * (0.55 + 0.45 * t)
            lay = Canvas(size, size)
            _blob(lay, cx, cy, r, DRED, wobble=2 + tier * 0.4, seed=f)
            _blob(lay, cx, cy, r * 0.85, RED, wobble=2, seed=f + 9)
            _blob(lay, cx, cy, r * 0.62, ORA, wobble=1.5, seed=f + 17)
            _blob(lay, cx, cy, r * 0.38 * (1.2 - t * 0.5), YEL, wobble=1, seed=f + 23)
            _disk(lay, cx - r * 0.2, cy - r * 0.25, max(1, r * 0.14), WHITE)   # hot highlight up-left
            fk.stack(c, lay, "#3a0e0e")
            for a, d, sp in embers:
                rr = r * d
                fk.streak(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr, math.cos(a), math.sin(a), 4, YEL, ORA)
            if tier >= 4:
                fk.ring_band(c, cx, cy, r + 3, [DRED, ORA, YEL])
        else:          # smoke rises, embers drift, then fade
            k = f - 4
            r = radius * (0.9 + 0.04 * k)
            _blob(c, cx, cy - k * 1.5, r * (0.8 - 0.05 * k), SMOKE, density=0.5 - 0.04 * k, wobble=3, seed=40 + k)
            _blob(c, cx, cy - k * 1.5, r * (0.55 - 0.05 * k), SMOKE_L, density=0.35, wobble=2, seed=50 + k)
            _blob(c, cx, cy, max(1, r * (0.35 - 0.04 * k)), ORA, wobble=1.5, seed=60 + k)
            for a, d, sp in embers:
                rr = radius * d * (1 + 0.1 * k)
                fk.streak(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr - k * sp * 2, 0, -1, 3, YEL if (k + int(a * 3)) % 2 else ORA, RED)
            if f >= 8:
                _fade(c, min(0.95, 0.1 + 0.2 * (f - 7)))
        out.append(c)
    return out


METEOR_MS = [90, 90, 60, 50, 50, 60, 70, 80, 110, 120, 120, 130, 140]


def meteor(tier, w, h, ground, radius, seed=5):
    """13 frames: warning, the outlined rock falls in a layered fire trail, a flash with
    rays and outlined debris, the crater smoulders with rising embers, fade."""
    import fxkit as fk
    cx, cy = w / 2, ground
    rng = random.Random(seed)
    rocks = [(rng.uniform(0, math.tau), rng.uniform(0.4, 1.0)) for _ in range(8 + 2 * tier)]
    embers = [(rng.uniform(0, math.tau), rng.uniform(0.2, 0.8)) for _ in range(8 + 2 * tier)]
    rr = 7 + tier * 1.4   # a big rock, readable while it falls
    out = []
    for f in range(13):
        c = Canvas(w, h)
        if f < 5:
            mark = radius * (0.5 + 0.12 * f)
            fk.ring_band(c, cx, cy, mark, [DRED, RED] if f % 2 else [RED, ORA])
            if f >= 2:
                t = (f - 1) / 4
                mx, my = cx + (1 - t) * w * 0.35, cy - (1 - t) * (h - 6) + rr
                for b, col in enumerate([DRED, RED, ORA, YEL]):   # trail: all rims first, then hotter cores
                    for k in range(8, 0, -1):
                        if b < (4 if k <= 3 else 3 if k <= 6 else 2):
                            _disk(c, mx + k * 3, my - k * 5, max(1.0, (rr * 1.7 - k * 0.8) * (1 - b * 0.24)), col)
                lay = Canvas(w, h)
                _disk(lay, mx, my, rr, ROCK)
                _disk(lay, mx - rr * 0.3, my - rr * 0.3, rr * 0.55, ROCK_L)
                _disk(lay, mx + rr * 0.35, my + rr * 0.35, rr * 0.4, ASH)
                fk.stack(c, lay, "#1a0e0e")
                _p(c, mx - rr * 0.5, my - rr * 0.6, YEL)
        elif f == 5:   # the hit
            fk.glow(c, cx, cy, radius * 0.7, [RED, ORA, YEL, WHITE], density=0.95)
            fk.rays(c, cx, cy, radius * 0.4, radius * 1.1, 12 + 2 * tier, YEL, WHITE, rot=0.15, width=2)
        elif f < 8:
            t = (f - 4) / 3
            r = radius * (0.6 + 0.4 * t)
            lay = Canvas(w, h)
            _blob(lay, cx, cy, r, DRED, wobble=3, seed=f)
            _blob(lay, cx, cy, r * 0.8, RED, wobble=2, seed=f + 3)
            _blob(lay, cx, cy, r * 0.55, ORA, wobble=2, seed=f + 5)
            _blob(lay, cx, cy, r * 0.3, YEL, wobble=1, seed=f + 7)
            fk.stack(c, lay, "#3a0e0e")
            lay = Canvas(w, h)
            for a, d in rocks:
                fk.crystal(lay, cx + math.cos(a) * r * (0.9 + d * t), cy + math.sin(a) * r * (0.9 + d * t) - 4 * t, a,
                           3 + tier * 0.5, 1.6, ROCK_L, ROCK, ASH, YEL)
            fk.stack(c, lay, "#1a0e0e")
            if tier >= 4:
                fk.ring_band(c, cx, cy, r + 3, [DRED, ORA, YEL])
        else:
            k = f - 8
            _disk(c, cx, cy, radius * 0.7, ASH, density=0.5)
            fk.ring_band(c, cx, cy, radius * 0.7, ["#1a0e0e", ROCK, ROCK_L])
            _blob(c, cx, cy, radius * 0.35, RED, density=0.7 - 0.08 * k, wobble=2, seed=70 + k)
            _blob(c, cx, cy, radius * 0.18, YEL if tier >= 5 else ORA, density=0.8, wobble=1, seed=80 + k)
            for a, d in embers:
                fk.streak(c, cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.6 - k * 3, 0, -1, 3, YEL, ORA)
            if k % 2 == 0:
                fk.sparkle(c, int(cx - radius * 0.2), int(cy - 4 - k), 2, WHITE, YEL)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
    return out
