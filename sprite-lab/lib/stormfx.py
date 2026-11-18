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


STORM_MS = [80, 80, 80, 60, 60, 60, 70, 100, 110, 120, 130]


def storm(tier, size, radius, seed=11):
    """11 frames: the cloud, three strike frames, sparks, fade (centre = ground target)."""
    cx = cy = size / 2
    rng = random.Random(seed)
    n = 2 + (tier + 1) // 2
    spots = [(cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8)
             for a, d in ((rng.uniform(0, math.tau), rng.uniform(0.1, 0.8)) for _ in range(n))]
    out = []
    for f in range(11):
        c = Canvas(size, size)
        if f < 3:   # cloud gathers, shadow on the ground
            t = (f + 1) / 3
            _disk(c, cx, cy, radius * 0.9 * t, CLOUD, density=0.25)
            for k in range(5 + tier):
                a = k * math.tau / (5 + tier) + f * 0.4
                _disk(c, cx + math.cos(a) * radius * 0.5 * t, cy + math.sin(a) * radius * 0.35 * t - 6, 3 + 2 * t, CLOUD_L, density=0.6)
            if f == 2:
                _p(c, cx, cy - 4, BOLT)
        elif f < 6:   # strikes: each frame a different set of bolts
            _disk(c, cx, cy, radius * 0.9, CLOUD, density=0.2)
            for i, (x, y) in enumerate(spots):
                if (i + f) % 2 == 0 or f == 4:
                    _bolt(c, x + rng.uniform(-3, 3), 0, x, y, rng, BOLT, GLOW)
                    _disk(c, x, y, 6 + tier, GLOW, density=0.5)
                    _disk(c, x, y, 3 + tier * 0.5, BOLT_M)
                    _disk(c, x, y, 1.5, BOLT)
            if tier >= 4:
                _ring(c, cx, cy, radius * (0.6 + 0.1 * (f - 3)), GLOW)
        else:          # sparks crawl, then fade
            k = f - 6
            for x, y in spots:
                for s in range(4 + tier):
                    a = s * 1.7 + k
                    r = 2 + k * 2 + (s % 3)
                    _p(c, x + math.cos(a) * r, y + math.sin(a) * r, SPARK if s % 2 else BOLT_M)
                _disk(c, x, y, max(1, 3 - k), GLOW, density=0.5)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.22 * k))
        out.append(c)
    return out


STOMP_MS = [50, 50, 55, 55, 60, 90, 100, 110, 120, 130]


def stomp(tier, size, radius, seed=13):
    """10 frames: a dust shock ring with cracks and stones, dust settles, fade."""
    cx = cy = size / 2
    rng = random.Random(seed)
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.5, 0.9)) for _ in range(5 + tier)]
    stones = [(rng.uniform(0, math.tau), rng.uniform(0.4, 1.0)) for _ in range(6 + 2 * tier)]
    out = []
    for f in range(10):
        c = Canvas(size, size)
        if f < 5:
            t = (f + 1) / 5
            rr = radius * (0.3 + 0.7 * t)
            for a, d in cracks:
                c.line(int(cx), int(cy), int(cx + math.cos(a) * rr * d), int(cy + math.sin(a) * rr * d * 0.8), DIRT_D)
            _ring(c, cx, cy, rr, DUST, 2)
            _ring(c, cx, cy, rr - 2, DUST_L)
            for k in range(10 + 2 * tier):
                a = k * math.tau / (10 + 2 * tier)
                _disk(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr, 2 + tier * 0.3, DUST_L if k % 2 else DUST, density=0.8)
            for a, d in stones:
                r = rr * d
                _p(c, cx + math.cos(a) * r, cy + math.sin(a) * r - 6 * math.sin(t * math.pi), STONE_L)
                _p(c, cx + math.cos(a) * r + 1, cy + math.sin(a) * r - 6 * math.sin(t * math.pi), STONE)
            if tier >= 4:
                _ring(c, cx, cy, rr * 0.55, DUST)
        else:
            k = f - 5
            for a, d in cracks:
                c.line(int(cx), int(cy), int(cx + math.cos(a) * radius * d), int(cy + math.sin(a) * radius * d * 0.8), DIRT)
            _disk(c, cx, cy, radius * (0.9 + 0.05 * k), DUST, density=0.3 - 0.05 * k)
            for a, d in stones:
                _p(c, cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d, STONE)
            _fade(c, min(0.95, 0.1 + 0.2 * k))
        out.append(c)
    return out


QUAKE_MS = [70, 70, 60, 60, 60, 70, 100, 110, 120, 130, 140]


def earthquake(tier, size, radius, seed=17):
    """11 frames: a rift opens across the target, rock spikes rise, it closes, fade."""
    cx = cy = size / 2
    rng = random.Random(seed)
    path = [(cx - radius + 2 * radius * k / 10, cy + rng.uniform(-radius * 0.25, radius * 0.25)) for k in range(11)]
    spikes = [path[k] for k in range(1, 10, 2)][: 2 + tier]
    out = []
    for f in range(11):
        c = Canvas(size, size)
        open_ = [0.2, 0.5, 1.0, 1.0, 1.0, 0.8, 0.5, 0.3, 0.2, 0.1, 0.05][f]
        _disk(c, cx, cy, radius * 0.9, DIRT, density=0.18 * min(1.0, f / 2 + 0.3))
        w = max(1, round(1 + 3 * open_ + tier * 0.3 * open_))
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            c.line(int(x0), int(y0), int(x1), int(y1), DIRT_D, w)
            if open_ > 0.6:
                c.line(int(x0), int(y0) - w, int(x1), int(y1) - w, "#ff8a2a" if tier >= 4 else DIRT)
        if 2 <= f <= 6:   # rock spikes
            h = (6 + tier * 2) * (1.0 if f < 6 else 0.5)
            for x, y in spikes:
                c.polygon([(int(x - 3), int(y)), (int(x + 3), int(y)), (int(x), int(y - h))], STONE)
                c.line(int(x), int(y), int(x - 1), int(y - h + 1), STONE_L)
        if 2 <= f <= 5:   # dust thrown up
            for k in range(8 + tier):
                x, y = path[k % len(path)]
                _p(c, x + rng.uniform(-3, 3), y - rng.uniform(2, 10), DUST_L)
        if f >= 7:
            _fade(c, min(0.95, 0.15 + 0.2 * (f - 6)))
        out.append(c)
    return out
