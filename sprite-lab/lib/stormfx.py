"""stormfx: lightning storm, ground slam (stomp) and earthquake at double pixel density.

Same contract as icefx / firefx: frames twice the old size, gen.py writes "px_scale": 0.5,
each effect has a lead-in, the hits, a lingering part and a dithered fade:
  storm:      a thundercloud gathers -> bolts strike -> sparks crawl on the ground -> fade
  stomp:      dust shock ring runs out, cracks, flying stones -> dust settles -> fade
  earthquake: the ground splits along a rift, rock spikes push up -> it closes -> fade
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
import fxkit as fk
from icefx import _disk, _fade, _p, _ring

CLOUD = "#3a3a5a"
CLOUD_L = "#5a5a80"
BOLT = "#fff8c0"
BOLT_M = "#ffe14a"
GLOW = "#9ad0ff"
SPARK = "#c8f0ff"
DUST = "#b89a70"
DUST_L = "#d8c09a"
DIRT = "#6a4a2a"
DIRT_D = "#3e2a18"
STONE = "#8a8070"
STONE_L = "#b8b0a0"


def _bolt(c, x0, y0, x1, y1, rng, col, glow, segs=7):
    pts = [(x0, y0)]
    for k in range(1, segs):
        t = k / segs
        pts.append((x0 + (x1 - x0) * t + rng.uniform(-4, 4), y0 + (y1 - y0) * t))
    pts.append((x1, y1))
    for (a, b), (cx, cy) in zip(pts, pts[1:]):
        c.line(int(a) - 1, int(b), int(cx) - 1, int(cy), glow, 3)   # glow either side
        c.line(int(a), int(b), int(cx), int(cy), col, 2)


def _spots_mask(size, spots, r):
    """Hit mask of a storm frame: disks where the bolts land (none between strikes)."""
    m = Canvas(size, size)
    for x, y in spots:
        if r > 0:
            m.ellipse(int(x - r), int(y - r), int(x + r), int(y + r), "#ffffff", fill=True)
    return m


STORM_MS = [80, 80, 80, 55, 55, 55, 55, 80, 100, 110, 120, 130]
STONE_D = "#4a4038"


def storm(tier, size, radius, seed=11):
    """12 frames: cloud gathers, four strike frames (outlined bolts, flash, sparkles),
    sparks crawl, fade."""
    import fxkit as fk
    cx = cy = size / 2
    rng = random.Random(seed)
    n = 2 + (tier + 1) // 2
    spots = [(cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8)
             for a, d in ((rng.uniform(0, math.tau), rng.uniform(0.1, 0.8)) for _ in range(n))]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        if f < 3:
            t = (f + 1) / 3
            _disk(c, cx, cy, radius * 0.9 * t, CLOUD, density=0.2)
            lay = Canvas(size, size)
            for k in range(5 + tier):
                a = k * math.tau / (5 + tier) + f * 0.4
                fk.glow(lay, cx + math.cos(a) * radius * 0.5 * t, cy + math.sin(a) * radius * 0.35 * t - 6, 4 + 2 * t, [CLOUD, CLOUD_L])
            fk.stack(c, lay, "#1a1a2e")
            if f == 2:
                fk.sparkle(c, int(cx), int(cy - 6), 3, BOLT, GLOW)
        elif f < 7:
            _disk(c, cx, cy, radius * 0.9, CLOUD, density=0.15)
            lay = Canvas(size, size)
            for i, (x, y) in enumerate(spots):
                if (i + f) % 2 == 0 or f == 4:
                    _bolt(lay, x + rng.uniform(-3, 3), 0, x, y, rng, BOLT, GLOW)
            fk.stack(c, lay, "#1a1a3a")
            for i, (x, y) in enumerate(spots):
                if (i + f) % 2 == 0 or f == 4:
                    fk.glow(c, x, y, 6 + tier, [GLOW, BOLT_M, BOLT], density=0.8)
                    fk.rays(c, x, y, 3, 8 + tier, 6, BOLT_M, BOLT, rot=f)
            if tier >= 4:
                fk.ring_band(c, cx, cy, radius * (0.6 + 0.08 * (f - 3)), [GLOW, SPARK])
        else:
            k = f - 7
            for x, y in spots:
                for s_ in range(4 + tier):
                    a = s_ * 1.7 + k
                    r = 2 + k * 2 + (s_ % 3)
                    fk.streak(c, x + math.cos(a) * r, y + math.sin(a) * r, math.cos(a), math.sin(a), 3, SPARK, GLOW)
                if k < 2:
                    fk.sparkle(c, int(x), int(y), 2, BOLT, GLOW)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.2 * k))
        out.append(c)
        masks.append(_spots_mask(size, spots, 6 + tier if 3 <= f < 7 else 0))
    return fk.FxFrames(out, masks)


STOMP_MS = [60, 45, 50, 55, 55, 60, 80, 90, 100, 110, 120, 130]


def stomp(tier, size, radius, seed=13):
    """12 frames: the foot lands (impact flash), a dust shock ring with cracks and
    outlined flying rocks, the dust settles, fade."""
    import fxkit as fk
    cx = cy = size / 2
    radius = min(radius, size / 2 - 5)
    rng = random.Random(seed)
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.5, 0.95)) for _ in range(5 + tier)]
    rocks = [(rng.uniform(0, math.tau), rng.uniform(0.4, 1.0)) for _ in range(6 + 2 * tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        if f == 0:
            fk.glow(c, cx, cy, radius * 0.3, [DUST, DUST_L, "#fff2d0"])
            fk.rays(c, cx, cy, radius * 0.25, radius * 0.6, 8, DUST_L, None)
        elif f < 6:
            t = f / 5
            rr = radius * (0.3 + 0.7 * t)
            for a, d in cracks:
                x1, y1 = cx + math.cos(a) * rr * d, cy + math.sin(a) * rr * d * 0.8
                c.line(int(cx), int(cy), int(x1), int(y1), DIRT_D, 2)
                c.line(int(cx), int(cy), int(x1), int(y1), DIRT)
            fk.ring_band(c, cx, cy, rr, [DIRT_D, DUST, DUST_L, "#fff2d0"])
            lay = Canvas(size, size)
            for k in range(10 + 2 * tier):
                a = k * math.tau / (10 + 2 * tier)
                fk.glow(lay, cx + math.cos(a) * rr, cy + math.sin(a) * rr, 2.5 + tier * 0.3, [DUST, DUST_L])
            for a, d in rocks:
                r = rr * d
                fk.crystal(lay, cx + math.cos(a) * r, cy + math.sin(a) * r - 7 * math.sin(t * math.pi), a - 1.2,
                           3 + tier * 0.6, 1.6, STONE_L, STONE, STONE_D, "#e8e0d0")
            fk.stack(c, lay, DIRT_D)
        else:
            k = f - 6
            for a, d in cracks:
                c.line(int(cx), int(cy), int(cx + math.cos(a) * radius * d), int(cy + math.sin(a) * radius * d * 0.8), DIRT)
            _disk(c, cx, cy - k, radius * (0.9 + 0.05 * k), DUST, density=0.28 - 0.04 * k)
            for a, d in rocks:
                _p(c, cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d, STONE)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_disk(size, size, cx, cy, radius * 0.3 if f == 0 else radius * (0.3 + 0.7 * f / 5) if f < 6 else radius * 0.9))
    return fk.FxFrames(out, masks)


QUAKE_MS = [70, 70, 60, 60, 60, 60, 70, 90, 100, 110, 120, 130]


def earthquake(tier, size, radius, seed=17):
    """12 frames: tremor cracks, the rift tears open with outlined rock spikes and
    thrown dust (lava glow from IV), it closes, fade."""
    import fxkit as fk
    cx = cy = size / 2
    rng = random.Random(seed)
    path = [(cx - radius + 2 * radius * k / 10, cy + rng.uniform(-radius * 0.25, radius * 0.25)) for k in range(11)]
    spikes = [path[k] for k in range(1, 10, 2)][: 2 + tier]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        open_ = [0.15, 0.3, 0.7, 1.0, 1.0, 1.0, 0.8, 0.5, 0.3, 0.2, 0.1, 0.05][f]
        _disk(c, cx, cy, radius * 0.9, DIRT, density=0.14 * min(1.0, f / 2 + 0.3))
        w = max(1, round(1 + 3 * open_ + tier * 0.3 * open_))
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            c.line(int(x0), int(y0), int(x1), int(y1), DIRT_D, w + 1)
            if open_ > 0.6:
                c.line(int(x0), int(y0), int(x1), int(y1), "#ff8a2a" if tier >= 4 else "#2a1a10", max(1, w - 1))
        if 2 <= f <= 7:
            h = (7 + tier * 2) * (1.0 if f < 7 else 0.6)
            lay = Canvas(size, size)
            for x, y in spikes:
                fk.crystal(lay, x, y, -math.pi / 2 + rng.uniform(-0.3, 0.3), h, 3, STONE_L, STONE, STONE_D, "#e8e0d0")
            fk.stack(c, lay, DIRT_D)
        if 2 <= f <= 6:
            for k in range(10 + tier):
                x, y = path[k % len(path)]
                fk.streak(c, x + rng.uniform(-3, 3), y - rng.uniform(2, 12), 0, -1, 3, DUST_L, DUST)
        if f >= 8:
            _fade(c, min(0.95, 0.15 + 0.2 * (f - 7)))
        out.append(c)
        masks.append(fk.mask_disk(size, size, cx, cy, radius * 0.9))
    return fk.FxFrames(out, masks)
