"""burstfx: projectile impacts, earth eruption, holy column and lightning strike, drawn to
the fx_craft standard (double density, >= 12 frames, lead-in -> hit -> linger -> fade,
fxkit solids). Palettes per skill keep each element readable:
  impact_burst(pal): charge spark -> flash and rays -> energy blob with outlined shards
                     -> sparks and a ring linger -> fade        (arcane, solar, thunder, void, steel)
  earth_burst:       cracks run out -> rock pillars erupt in a ring -> dust -> crumble
  holy_column:       a glyph circle on the ground -> the beam slams down -> pillar shimmers -> fades up
  lightning_strike:  a crackling spark above -> the bolt hits with a flash -> crackle -> fade
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
from icefx import _disk, _fade, _p
import fxkit as fk

PALS = {
    # rim, mid, light, core, shard lit, shard dark, outline
    "arcane": ("#4a2a9a", "#7a5af0", "#7ef0ff", "#ffffff", "#c8f6ff", "#4a2a9a", "#1a1040"),
    "solar": ("#a8601a", "#ffb43a", "#ffe88a", "#fffbe0", "#fff2a8", "#c8802a", "#3a2008"),
    "thunder": ("#2a6ab0", "#ffe14a", "#fff8c0", "#ffffff", "#fff8c0", "#2a6ab0", "#101a40"),
    "void": ("#2a0a4a", "#8a2ad8", "#e05aff", "#ffd8ff", "#e8a0ff", "#3a0a6a", "#0a0418"),
    "steel": ("#5f7186", "#9fb3c8", "#e8f0f6", "#ffffff", "#f2f7fb", "#5f7186", "#1b1726"),
}
IMPACT_MS = [50, 45, 50, 55, 60, 70, 80, 90, 100, 110, 120, 130]


def impact_burst(tier, size, radius, pal, seed=21):
    rim, mid, light, core, lit, dark, outl = PALS[pal]
    cx = cy = size / 2
    radius = min(radius, size / 2 - 4)
    rng = random.Random(seed)
    shards = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(6 + 2 * tier)]
    sparks = [(rng.uniform(0, math.tau), rng.uniform(0.5, 1.1)) for _ in range(10 + 3 * tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        if f == 0:
            fk.glow(c, cx, cy, radius * 0.25, [mid, light, core])
            fk.sparkle(c, int(cx), int(cy), 2 + tier, core, light)
        elif f == 1:
            fk.glow(c, cx, cy, radius * 0.55, [mid, light, core], density=0.9)
            fk.rays(c, cx, cy, radius * 0.35, radius, 8 + 2 * tier, light, core, rot=0.3, width=2)
        elif f < 5:
            t = (f - 1) / 3
            r = radius * (0.5 + 0.5 * t)
            fk.glow(c, cx, cy, r, [rim, mid, light, core], density=0.85 - 0.15 * t)
            lay = Canvas(size, size)
            for a, d in shards:
                fk.crystal(lay, cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6, a, (3 + tier) * d * (0.7 + 0.5 * t),
                           1.6 + tier * 0.2, lit, mid, dark, core)
            fk.stack(c, lay, outl)
            fk.ring_band(c, cx, cy, r + 2, [outl, rim, light])
            for a, d in sparks:
                rr = r * d + 3 * t
                fk.streak(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr, math.cos(a), math.sin(a), 3, core, light)
        else:
            k = f - 5
            r = radius * (1.0 + 0.04 * k)
            fk.ring_band(c, cx, cy, r, [rim, mid])
            fk.glow(c, cx, cy, max(1, r * (0.35 - 0.04 * k)), [mid, light], density=0.6)
            for a, d in sparks:
                rr = r * d * (1 + 0.08 * k)
                if (k + int(a * 5)) % 3:
                    _p(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr - k, light)
            if k % 2 == 0 and k < 4:
                fk.sparkle(c, int(cx + r * 0.4), int(cy - r * 0.3), 2, core, light)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_disk(size, size, cx, cy, radius * 0.25 if f == 0 else radius * 0.55 if f == 1 else radius * (0.5 + 0.5 * (f - 1) / 3) if f < 5 else radius * 0.4))
    return fk.FxFrames(out, masks)


STONE = ("#b8b0a0", "#8a8070", "#4a4038", "#e8e0d0")
DIRT = "#6a4a2a"
DIRT_D = "#3e2a18"
DUST = "#b89a70"
DUST_L = "#d8c09a"
EARTH_MS = [70, 60, 55, 55, 60, 70, 80, 90, 100, 110, 120, 130]


def earth_burst(tier, size, radius, seed=31):
    cx = cy = size / 2
    radius = min(radius, size / 2 - 6)
    rng = random.Random(seed)
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(6 + tier)]
    pillars = [(k * math.tau / (5 + tier) + rng.uniform(-0.2, 0.2), rng.uniform(0.35, 0.8)) for k in range(5 + tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        grow = min(1.0, (f + 1) / 3)
        for a, d in cracks:
            x1, y1 = cx + math.cos(a) * radius * d * grow, cy + math.sin(a) * radius * d * grow * 0.8
            c.line(int(cx), int(cy), int(x1), int(y1), DIRT_D, 2)
            c.line(int(cx), int(cy), int(x1), int(y1), DIRT)
        if f == 1:
            fk.glow(c, cx, cy, radius * 0.25, [DUST, DUST_L, "#fff2d0"])
        if 2 <= f <= 7:
            up = [0.5, 1.0, 1.0, 0.9, 0.7, 0.4][f - 2]
            lay = Canvas(size, size)
            for a, d in pillars:
                x, y = cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8
                fk.crystal(lay, x, y + 3, -math.pi / 2 + (a % 0.5) - 0.25, (12 + tier * 3) * up, 4 + tier * 0.4, *STONE)
            fk.stack(c, lay, DIRT_D)
            if f <= 4:
                for a, d in pillars:
                    x, y = cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8
                    fk.streak(c, x + rng.uniform(-3, 3), y - rng.uniform(4, 12), 0, -1, 3, DUST_L, DUST)
        if f >= 6:
            _disk(c, cx, cy - (f - 6), radius * 0.8, DUST, density=0.22 - 0.03 * (f - 6))
        if f >= 8:
            _fade(c, min(0.95, 0.1 + 0.2 * (f - 7)))
        out.append(c)
        masks.append(fk.mask_disk(size, size, cx, cy, radius * 0.85))
    return fk.FxFrames(out, masks)


HOLY_MS = [80, 70, 60, 50, 55, 60, 80, 90, 100, 110, 120, 130]
GOLD = ("#a8802f", "#ffd04a", "#fff2a8", "#ffffff")


def holy_column(tier, w, h, ground, radius, seed=41):
    cx = w / 2
    rng = random.Random(seed)
    motes = [(rng.uniform(-1, 1), rng.uniform(0, 1)) for _ in range(10 + 3 * tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    bw = radius * 0.55
    for f in range(12):
        c = Canvas(w, h)
        gl = min(1.0, (f + 1) / 2)
        fk.ring_band(c, cx, ground, radius * 0.9 * gl, [GOLD[0], GOLD[1]])   # glyph circle
        if tier >= 3:
            for k in range(6):
                a = k * math.pi / 3 + f * 0.1
                fk.sparkle(c, int(cx + math.cos(a) * radius * 0.9 * gl), int(ground + math.sin(a) * radius * 0.45 * gl), 1, GOLD[3], GOLD[1])
        if f in (2, 3):   # the beam slams down
            reach = h * (0.5 if f == 2 else 1.0)
            for x in range(int(cx - bw), int(cx + bw) + 1):
                col = GOLD[3] if abs(x - cx) < bw * 0.35 else (GOLD[2] if abs(x - cx) < bw * 0.7 else GOLD[1])
                c.line(x, int(ground - reach), x, int(ground), col)
            if f == 3:
                fk.rays(c, cx, ground, radius * 0.3, radius * 1.1, 10 + tier, GOLD[2], GOLD[3], width=2)
        elif 4 <= f <= 7:   # pillar shimmers, thinning
            k = f - 4
            bwk = bw * (1 - 0.15 * k)
            for x in range(int(cx - bwk), int(cx + bwk) + 1):
                col = GOLD[3] if abs(x - cx) < bwk * 0.3 else (GOLD[2] if (x + f) % 3 else GOLD[1])
                c.line(x, 0, x, int(ground), col)
            for mx, my in motes:
                fk.streak(c, cx + mx * bw * 1.4, ground - (my * h + k * 6) % h, 0, -1, 3, GOLD[3], GOLD[2])
        elif f >= 8:
            k = f - 8
            for mx, my in motes:
                _p(c, cx + mx * bw * 1.6, ground - (my * h * 0.6 + k * 8), GOLD[2])
            fk.glow(c, cx, ground, radius * 0.4, [GOLD[1], GOLD[2]], density=0.4)
            _fade(c, min(0.95, 0.15 + 0.2 * k))
        out.append(c)
        masks.append(fk.mask_disk(w, h, cx, ground, radius * 0.9))
    return fk.FxFrames(out, masks)


BOLT_MS = [70, 70, 50, 50, 55, 60, 80, 90, 100, 110, 120, 130]


def lightning_strike(tier, w, h, ground, radius, seed=51):
    cx = w / 2
    rng = random.Random(seed)
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(w, h)
        if f < 2:   # a crackling spark gathers at the top, a mark on the ground
            fk.sparkle(c, int(cx + rng.uniform(-3, 3)), 6 + f * 2, 3 + tier, "#fff8c0", "#9ad0ff")
            fk.ring_band(c, cx, ground, radius * (0.4 + 0.2 * f), ["#2a6ab0", "#9ad0ff"])
        elif f < 6:
            lay = Canvas(w, h)
            x0 = cx + rng.uniform(-6, 6)
            pts = [(x0, 0)]
            segs = 9
            for k in range(1, segs):
                pts.append((cx + rng.uniform(-8, 8) * (1 - k / segs), ground * k / segs))
            pts.append((cx, ground))
            for (a, b), (x1, y1) in zip(pts, pts[1:]):
                lay.line(int(a), int(b), int(x1), int(y1), "#9ad0ff", 4 + tier // 2)
                lay.line(int(a), int(b), int(x1), int(y1), "#fff8c0", 2)
            if tier >= 3:   # side forks
                for k in (3, 5):
                    a, b = pts[k]
                    lay.line(int(a), int(b), int(a + rng.choice((-1, 1)) * 10), int(b + 8), "#fff8c0", 1)
            fk.stack(c, lay, "#101a40")
            fk.glow(c, cx, ground, radius * (0.7 if f == 2 else 0.5), ["#2a6ab0", "#9ad0ff", "#fff8c0", "#ffffff"], density=0.85)
            fk.rays(c, cx, ground, radius * 0.3, radius, 8 + tier, "#fff8c0", "#ffffff", rot=f * 0.4, width=2 if f == 2 else 1)
        else:
            k = f - 6
            for s in range(6 + tier):
                a = s * 1.3 + k * 0.8
                r = radius * (0.3 + 0.12 * k) * (0.6 + (s % 3) * 0.2)
                fk.streak(c, cx + math.cos(a) * r, ground + math.sin(a) * r * 0.6, math.cos(a), math.sin(a), 3, "#c8f0ff", "#2a6ab0")
            if k < 3:
                fk.sparkle(c, int(cx), int(ground), 3 - k, "#ffffff", "#9ad0ff")
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_disk(w, h, cx, ground, radius * 0.5 if 2 <= f <= 3 else 0))
    return fk.FxFrames(out, masks)
