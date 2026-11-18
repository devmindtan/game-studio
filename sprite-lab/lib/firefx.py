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
import fxkit as fk
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
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
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
        masks.append(fk.mask_disk(size, size, cx, cy, radius * 0.3 if f == 0 else radius * 0.6 if f == 1 else radius * (0.55 + 0.45 * (f - 1) / 3) * 0.85 if f <= 4 else radius * 0.5))
    return fk.FxFrames(out, masks)


METEOR_MS = [90, 90, 60, 50, 50, 60, 70, 80, 110, 120, 120, 130, 140]
LAVA = "#ff6a1a"
HOT = "#fff4d0"


def _rock(c, x, y, r, tier, rng_seed, outline="#1a0e0e"):
    """An irregular faceted rock (lit facet up-left, shade down-right); lava veins from II,
    a white-hot core from IV."""
    import fxkit as fk
    rng = random.Random(rng_seed)
    pts = [(x + math.cos(k * math.tau / 9) * r * rng.uniform(0.75, 1.1), y + math.sin(k * math.tau / 9) * r * rng.uniform(0.75, 1.1)) for k in range(9)]
    lay = Canvas(c.width, c.height)
    lay.polygon([(int(px), int(py)) for px, py in pts], ROCK)
    lay.polygon([(int(px), int(py)) for px, py in pts[4:8]] + [(int(x), int(y))], ASH)
    lay.polygon([(int(px), int(py)) for px, py in pts[0:1] + pts[5:9]] + [(int(x - r * 0.1), int(y - r * 0.1))], ROCK_L)
    if tier >= 2:   # glowing lava veins
        for k in range(1 + tier // 2):
            a = rng.uniform(0, math.tau)
            lay.line(int(x), int(y), int(x + math.cos(a) * r * 0.8), int(y + math.sin(a) * r * 0.8), LAVA)
    if tier >= 4:
        _disk(lay, x, y, r * 0.3, YEL)
        _disk(lay, x, y, r * 0.15, HOT)
    fk.stack(c, lay, outline)


def _flame(c, x, y, dx, dy, length, width, cols):
    """A tapered flame trailing back from (x, y) along -(dx, dy): nested layers, outer first."""
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    px, py = -uy, ux
    for k, col in enumerate(cols):
        f = 1 - k / (len(cols) + 0.5)
        L, W = length * f, width * f
        tip = (x - ux * L, y - uy * L)
        c.polygon([(int(x + px * W), int(y + py * W)), (int(x - px * W), int(y - py * W)), (int(tip[0]), int(tip[1]))], col)


def _tongue(c, x, y, h, w, sway, cols):
    """An upward flame tongue on the ground (fire pillars, burning crater)."""
    for k, col in enumerate(cols):
        f = 1 - k * 0.3
        c.polygon([(int(x - w * f), int(y)), (int(x + w * f), int(y)), (int(x + sway), int(y - h * f))], col)


def meteor(tier, w, h, ground, radius, seed=5):
    """13 frames: warning -> the meteor(s) fall -> flash -> burst -> crater burns -> fade.
    Each tier adds its own mark (table in design/gameplay-rules.md is the standard; the
    tiers: I rock, II lava veins + fissures, III three meteors + shock ring + flame
    tongues, IV white-hot core + fire pillars, V a comet with aura, two rings, a sea of fire)."""
    import fxkit as fk
    cx, cy = w / 2, ground
    rng = random.Random(seed)
    rocks = [(rng.uniform(0, math.tau), rng.uniform(0.4, 1.0)) for _ in range(8 + 2 * tier)]
    embers = [(rng.uniform(0, math.tau), rng.uniform(0.2, 0.9)) for _ in range(8 + 3 * tier)]
    fissures = [(rng.uniform(0, math.tau), rng.uniform(0.7, 1.15)) for _ in range(3 + tier)]
    rr = 6 + tier * 1.5
    trail_cols = [DRED, RED, ORA, YEL] + ([HOT] if tier >= 4 else [])
    tw = rr * (1.0 + 0.15 * tier)
    # (land frame, ground offset x, y, scale): the main rock lands on frame 5 (the hit);
    # escorts land at their own moments, one before and one after (user 2026-11-18)
    falls = [(5, 0, 0, 1.0)] + ([(4, -26, 8, 0.5), (7, 22, -6, 0.45)] if tier >= 3 else [])
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)

    def falling(c, f):
        for land, ox, oy, k in falls:
            t = (f - (land - 4)) / 4.0   # 0 at the top of the frame .. 1 on landing
            ex, ey = cx + ox, cy + oy
            if 0.0 < t < 1.0:
                sx, sy = min(w - rr * k - 2, ex + w * 0.42), rr * k + 2
                mx, my = sx + (ex - sx) * t, sy + (ey - sy) * t
                dx, dy = ex - sx, ey - sy                   # the trail streams back along the real path
                flick = 0.85 + 0.15 * math.sin(f * 2.3 + land)
                if tier >= 5 and k == 1.0:
                    fk.glow(c, mx, my, rr * 2.2, [DRED, RED, ORA], density=0.45)
                _flame(c, mx, my, dx, dy, rr * k * (5.0 + 0.6 * tier) * flick, tw * k * (0.9 + 0.2 * flick), trail_cols)
                d = math.hypot(dx, dy)
                for e in range(3 + tier):   # embers shed behind it
                    back = (e + 1) * 4 + (f * 3 + e * 5) % 6
                    fk.streak(c, mx - dx / d * back + ((e * 7) % 5 - 2), my - dy / d * back, dx, dy, 3, YEL, ORA)
                _rock(c, mx, my, rr * k, tier if k == 1.0 else max(1, tier - 2), seed + land)
            elif k < 1.0 and land <= f <= land + 1:   # an escort's own small impact
                fk.glow(c, ex, ey, rr * 1.6 * (1.2 if f == land else 0.8), [DRED, RED, ORA, YEL])
                if f == land:
                    fk.rays(c, ex, ey, rr * 0.6, rr * 2.2, 8, YEL, HOT)

    for f in range(13):
        c = Canvas(w, h)
        if f < 5:
            mark = radius * (0.5 + 0.12 * f)
            fk.ring_band(c, cx, cy, mark, [DRED, RED] if f % 2 else [RED, ORA])
            falling(c, f)
        elif f == 5:
            fk.glow(c, cx, cy, radius * (0.6 + 0.06 * tier), [RED, ORA, YEL, HOT], density=0.95)
            fk.rays(c, cx, cy, radius * 0.35, radius * (0.9 + 0.08 * tier), 10 + 3 * tier, YEL, HOT, rot=0.15, width=2)
            if tier >= 5:
                fk.ring_band(c, cx, cy, radius * 1.05, [HOT, YEL])
        elif f < 8:
            t = (f - 4) / 3
            r = radius * (0.6 + 0.4 * t)
            if tier >= 2:   # lava fissures run out
                for a, d in fissures:
                    x1, y1 = cx + math.cos(a) * r * d, cy + math.sin(a) * r * d * 0.8
                    c.line(int(cx), int(cy), int(x1), int(y1), DRED, 3)
                    c.line(int(cx), int(cy), int(x1), int(y1), LAVA)
            if tier >= 3:
                fk.ring_band(c, cx, cy, r * 1.15, [DRED, ORA, YEL])
            if tier >= 5:
                fk.ring_band(c, cx, cy, r * 0.75, [ORA, YEL])
            lay = Canvas(w, h)
            _blob(lay, cx, cy, r * 0.85, DRED, wobble=3, seed=f)
            _blob(lay, cx, cy, r * 0.68, RED, wobble=2, seed=f + 3)
            _blob(lay, cx, cy, r * 0.48, ORA, wobble=2, seed=f + 5)
            _blob(lay, cx, cy, r * 0.26, YEL, wobble=1, seed=f + 7)
            fk.stack(c, lay, "#3a0e0e")
            if tier >= 4:   # fire pillars round the blast
                for k in range(6):
                    a = k * math.tau / 6 + 0.3
                    _tongue(c, cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8, 10 + 3 * tier, 3, (f % 2) * 2 - 1, [RED, ORA, YEL])
            lay = Canvas(w, h)
            for a, d in rocks:
                fk.crystal(lay, cx + math.cos(a) * r * (0.9 + d * t), cy + math.sin(a) * r * (0.9 + d * t) - 4 * t, a,
                           3 + tier * 0.6, 1.8, ROCK_L, ROCK, ASH, YEL)
            fk.stack(c, lay, "#1a0e0e")
        else:
            k = f - 8
            _disk(c, cx, cy, radius * 0.72, ASH, density=0.55)
            fk.ring_band(c, cx, cy, radius * 0.72, ["#1a0e0e", ROCK, ROCK_L])
            if tier >= 2:
                for a, d in fissures:
                    c.line(int(cx), int(cy), int(cx + math.cos(a) * radius * d * 0.7), int(cy + math.sin(a) * radius * d * 0.55), LAVA)
                pool = radius * (0.18 + 0.05 * tier)
                fk.glow(c, cx, cy, pool, [DRED, LAVA, YEL], density=0.9)
            else:
                _blob(c, cx, cy, radius * 0.25, RED, density=0.7, wobble=1, seed=80 + k)
            if tier >= 3:   # flame tongues flicker round the crater
                n_t = 4 + 2 * (tier - 3) + (6 if tier >= 5 else 0)
                for j in range(n_t):
                    a = j * math.tau / n_t + 0.2
                    hh = (6 + tier * 2) * (0.6 + 0.4 * ((j + k) % 2)) * (1 - 0.15 * k)
                    _tongue(c, cx + math.cos(a) * radius * 0.55, cy + math.sin(a) * radius * 0.4, hh, 2.5, (j + k) % 3 - 1, [RED, ORA, YEL])
            for a, d in embers:
                fk.streak(c, cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.6 - k * 3, 0, -1, 3, YEL, ORA)
            if k % 2 == 0:
                fk.sparkle(c, int(cx - radius * 0.2), int(cy - 4 - k), 2, HOT, YEL)
            if k >= 1:
                _fade(c, min(0.95, 0.08 + 0.17 * k))
        if 5 <= f <= 8:
            falling(c, f)
        out.append(c)
        masks.append(fk.mask_disk(w, h, cx, cy, radius * 0.6 if f == 5 else radius * (0.6 + 0.4 * (f - 4) / 3) * 0.85 if f in (6, 7) else 0))
    return fk.FxFrames(out, masks)
