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
from icefx import _disk, _fade, _p


def _alpha_fade(c, amount):
    """Fades the whole frame by lowering its alpha (no checkerboard holes: review 2026-11-21, the dithered fade
    read as a dot cloud over the boss / hero)."""
    px = c.img.load()
    k = 1.0 - amount
    for y in range(c.height):
        for x in range(c.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (r, g, b, int(a * k))

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
    """No dithered veil over the area (user 2026-11-21: the purple wash hid the field).
    12 frames: cloud gathers, four strike frames (outlined bolts, flash, sparkles),
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
            lay = Canvas(size, size)
            for k in range(5 + tier):
                a = k * math.tau / (5 + tier) + f * 0.4
                fk.glow(lay, cx + math.cos(a) * radius * 0.5 * t, cy + math.sin(a) * radius * 0.35 * t - 6, 4 + 2 * t, [CLOUD, CLOUD_L])
            fk.stack(c, lay, "#1a1a2e")
            if f == 2:
                fk.sparkle(c, int(cx), int(cy - 6), 3, BOLT, GLOW)
        elif f < 7:
            lay = Canvas(size, size)
            import boltfx
            for i, (x, y) in enumerate(spots):
                if (i + f) % 2 == 0 or f == 4:   # thin bolt from its own small dark cloud (user 2026-11-18)
                    top = max(8.0, y - size * 0.55)
                    boltfx.thin_bolt(lay, x + rng.uniform(-2, 2), top + 5, x, y, rng, tier)
                    boltfx.dark_cloud(lay, x, top, 5 + tier * 0.6, flash=f == 4)
            fk.stack(c, lay, None)
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
        mk = Canvas(size, size)
        if 3 <= f < 7:   # the art around each landing point (its flash and rays), not the bolt shafts
            for x, y in spots:
                mk.img.alpha_composite(fk.mask_art(c, x, y, 9 + tier * 1.5).img)
        masks.append(mk)
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
            # dust settles as soft puffs along the rim, rising and shrinking; the middle stays clear (review
            # 2026-11-21: a dithered dust disk covered the boss / hero standing in it)
            n = 8 + 2 * tier
            for q in range(n):
                a = q * math.tau / n + 0.3
                pr = max(1.0, 3.2 + tier * 0.3 - 0.6 * k)
                fk.glow(c, cx + math.cos(a) * radius * 0.92, cy + math.sin(a) * radius * 0.92 * 0.8 - 2 * k, pr, [DUST, DUST_L])
            for a, d in rocks:
                _p(c, cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d, STONE)
            if k >= 1:
                _alpha_fade(c, min(0.9, 0.15 + 0.2 * k))
        out.append(c)
        masks.append(fk.mask_art(c, cx, cy, radius * 0.35 if f == 0 else radius * (0.3 + 0.7 * f / 5) + 4 if f < 6 else radius))
    return fk.FxFrames(out, masks)


QUAKE_MS = [70, 70, 60, 60, 60, 60, 70, 90, 100, 110, 120, 130]


def _qnoise(x, y, salt=0):
    """A stable 0..1 scatter value (burstfx._h01 idea, kept local to stormfx)."""
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _scuff(c, cx, cy, r, seed, col=DIRT, density=0.6):
    """Churned earth: an uneven blot with a ragged edge, not a filled disc."""
    ri = int(math.ceil(r))
    for y in range(-ri, ri + 1):
        for x in range(-ri, ri + 1):
            dd = math.hypot(x, y) / max(1.0, r)
            a = math.atan2(y, x)
            wob = 0.87 + 0.11 * math.sin(a * 4 + seed) + 0.05 * math.sin(a * 9 - seed)
            if dd > wob:
                continue
            px, py = int(cx + x), int(cy + y)
            if _qnoise(px, py, seed + 7) < density * (1.05 - 0.85 * dd * dd):
                _p(c, px, py, col)


def _rift(c, path, open_, tier, f, seed):
    """A widening fissure: jagged, crumbling lips, a dark core and a heart that
    flickers instead of a solid stripe (user 2026-11-18: the old line was rigid)."""
    n = len(path)
    for i in range(n - 1):
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        taper = math.sin(math.pi * i / (n - 1)) ** 0.6   # narrow at the ends
        w = max(0.6, (0.9 + 3.2 * open_ + tier * 0.3 * open_) * taper)
        steps = max(3, int(math.hypot(x1 - x0, y1 - y0)))
        for s in range(steps + 1):
            t = s / steps
            jx = (_qnoise(i * 17 + s, f, 3) - 0.5) * 1.2 * open_
            jy = (_qnoise(i * 19 + s, f, 5) - 0.5) * 1.4 * open_
            px = int(round(x0 + (x1 - x0) * t + jx))
            py = int(round(y0 + (y1 - y0) * t + jy))
            for q in range(-int(math.ceil(w)), int(math.ceil(w)) + 1):
                if _qnoise(px + q, py, seed + 11) < 0.82 - 0.22 * abs(q) / max(1.0, w):
                    _p(c, px + q, py, DIRT_D)
            _p(c, px, py, "#1a1008")                     # the deep crack
            if open_ > 0.5 and _qnoise(px, py, seed + f * 3) < 0.20 + 0.35 * open_:
                _p(c, px, py - 1, "#ff8a2a" if tier >= 4 else "#2a1a10")


def earthquake(tier, size, radius, seed=17):
    """12 frames: tremor cracks, the rift tears open with rock spikes and thrown
    dust (lava glow from IV), it closes, fade. Tier ideas and timing unchanged."""
    import fxkit as fk
    cx = cy = size / 2
    rng = random.Random(seed)
    path = [(cx - radius + 2 * radius * k / 10, cy + rng.uniform(-radius * 0.25, radius * 0.25)) for k in range(11)]
    spikes = [path[k] for k in range(1, 10, 2)][: 2 + tier]
    # late tiers split the ground further: III grows one branch, IV two (with
    # lava in the cracks), V three. The main rift and all earlier tiers stay.
    branches = []
    if tier >= 3:
        for j in range(tier - 1):         # III:2, IV:3, V:4 branches
            sx, sy = path[3 + (j * 2) % 5]
            a = (0.7 + j * 0.85) if j % 2 == 0 else -(0.7 + j * 0.85)
            length = radius * (0.44 + 0.07 * j)
            bp = [(sx, sy)]
            for s in range(1, 5):
                t = s / 4.0
                bp.append((sx + math.cos(a) * length * t + rng.uniform(-1.5, 1.5),
                           sy + math.sin(a) * length * t * 0.7 + rng.uniform(-1.5, 1.5)))
            branches.append(bp)
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        mk = Canvas(size, size)   # damage mask: the rift, not the dust around it
        open_ = [0.15, 0.3, 0.7, 1.0, 1.0, 1.0, 0.8, 0.5, 0.3, 0.2, 0.1, 0.05][f]
        _scuff(c, cx, cy, radius * 0.9, seed + f % 3, DIRT, 0.13 * min(1.0, f / 2 + 0.3))
        _rift(c, path, open_, tier, f, seed)
        _rift(mk, path, open_, tier, f, seed)
        for j, bp in enumerate(branches):
            strength = open_ * (0.80 if tier < 5 else 0.95)
            _rift(c, bp, strength, tier, f, seed + 70 + j)
            _rift(mk, bp, strength, tier, f, seed + 70 + j)
        if 2 <= f <= 7:
            h = (7 + tier * 2) * (1.0 if f < 7 else 0.6)
            lay = Canvas(size, size)
            for x, y in spikes:
                fk.crystal(lay, x, y, -math.pi / 2 + rng.uniform(-0.3, 0.3), h, 3, STONE_L, STONE, STONE_D, "#e8e0d0")
            fk.stack(c, lay, DIRT_D)
            for x, y in spikes:   # a couple of crumbs at the foot of each shard
                for _ in range(2):
                    px, py = int(x + rng.uniform(-4, 4)), int(y + rng.uniform(-1, 3))
                    if _qnoise(px, py, f + 41) < 0.7:
                        _p(c, px, py, DIRT_D)
        if 2 <= f <= 6:
            # the rift is the story: only a few motes of dust, not a cloud
            for k in range(5 + tier // 2):
                x, y = path[k % len(path)]
                dx, dy = rng.uniform(-4, 4), -rng.uniform(2, 9) * (1 - 0.09 * (f - 2))
                px, py = int(x + dx), int(y + dy)
                if _qnoise(px, py, f + 31) < 0.6:
                    _p(c, px, py, DUST_L)
        if f >= 8:
            _fade(c, min(0.95, 0.15 + 0.2 * (f - 7)))
        out.append(c)
        masks.append(mk)   # a flat horizontal hit area along the fissure
    return fk.FxFrames(out, masks)
