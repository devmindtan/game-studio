"""icefx: hand-tuned ice AoE effects at double pixel density (frost nova, blizzard).

User 2026-11-18: the Scale2x smoothing looked wrong, and frost nova / blizzard popped
in and out with no ending. These effects are drawn on a frame twice the old size and
written with "px_scale": 0.5, so the game shows them at the same size on screen with
twice the real pixels. Each has phases with their own timing:
  frost nova: gather (cold motes spiral in) -> burst (ring and shards) -> frozen
              ground lingers (cracks, spikes, shimmer) -> shatter and fade (dither)
  blizzard:   form (arms grow) -> swirl (rotating snow arms, orbiting flakes) ->
              dissipate (arms dither away, flakes fly out)
Fades remove pixels with a 4x4 Bayer pattern (pixel-art fade, no alpha blending).
Tiers 1..5 add detail: petals (2+), standing spikes (3+), floor runes (4+), a big
six-branch snowflake (5); blizzard gets more arms and orbiting shards.
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas

CORE = "#ffffff"
ICE = "#c8f6ff"
ICE_M = "#6fe0ff"
ICE_D = "#2a8fd6"
DEEP = "#1b4f8a"
NIGHT = "#122a52"
FROST = "#9fe8ff"
SNOW = "#eaf9ff"

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def _p(c, x, y, col):
    xi, yi = int(round(x)), int(round(y))
    if 0 <= xi < c.width and 0 <= yi < c.height:
        c.pixel(xi, yi, col)


def _disk(c, cx, cy, r, col, density=1.0):
    """Filled disk; density < 1 keeps only part of the pixels (ordered dither)."""
    ri = int(math.ceil(r))
    for y in range(-ri, ri + 1):
        for x in range(-ri, ri + 1):
            if x * x + y * y <= r * r:
                px, py = int(cx + x), int(cy + y)
                if BAYER[py % 4][px % 4] < density * 16:
                    _p(c, px, py, col)


def _ring(c, cx, cy, r, col, width=1):
    for k in range(width):
        rr = r - k
        if rr > 0:
            c.ellipse(int(cx - rr), int(cy - rr), int(cx + rr), int(cy + rr), col, fill=False)


def _shard(c, cx, cy, a, r, length, col, tip):
    """A small ice triangle pointing outward at angle a, base at radius r."""
    bx, by = cx + math.cos(a) * r, cy + math.sin(a) * r
    tx, ty = cx + math.cos(a) * (r + length), cy + math.sin(a) * (r + length)
    px, py = -math.sin(a) * length * 0.35, math.cos(a) * length * 0.35
    c.polygon([(int(round(bx + px)), int(round(by + py))), (int(round(bx - px)), int(round(by - py))),
               (int(round(tx)), int(round(ty)))], col)
    _p(c, tx, ty, tip)


def _fade(c, amount):
    """Removes a share [amount] of the pixels in a Bayer pattern (0 = none, 1 = all)."""
    if amount <= 0:
        return c
    px = c.img.load()
    for y in range(c.height):
        for x in range(c.width):
            if px[x, y][3] and BAYER[y % 4][x % 4] < amount * 16:
                px[x, y] = (0, 0, 0, 0)
    return c


def _spike(c, cx, cy, h, w):
    """A standing ice crystal (seen from the side) on the ground at (cx, cy)."""
    c.polygon([(int(cx - w), int(cy)), (int(cx + w), int(cy)), (int(cx), int(cy - h))], ICE_M)
    c.line(int(cx), int(cy), int(cx), int(cy - h), CORE)
    _p(c, cx - w, cy, DEEP)
    _p(c, cx + w, cy, ICE_D)


def _snowflake(c, cx, cy, r, rot, col, tip):
    for k in range(6):
        a = rot + k * math.pi / 3
        ex, ey = cx + math.cos(a) * r, cy + math.sin(a) * r
        c.line(int(cx), int(cy), int(round(ex)), int(round(ey)), col)
        for f in (0.45, 0.7):
            bx, by = cx + math.cos(a) * r * f, cy + math.sin(a) * r * f
            for s in (-1, 1):
                b = a + s * 0.7
                c.line(int(round(bx)), int(round(by)), int(round(bx + math.cos(b) * r * 0.22)),
                       int(round(by + math.sin(b) * r * 0.22)), col)
        _p(c, ex, ey, tip)


# --- frost nova -----------------------------------------------------------------

FROST_MS = [70, 70, 70, 70, 50, 55, 60, 65, 110, 110, 110, 110, 90, 90, 100, 120]
OUT = "#0c1830"   # dark outline of solid ice


def frost_nova(tier, size, radius, seed=1):
    """16 frames: gather -> flash and crystal burst -> crystal crown lingers -> shatters.
    Built from fxkit pieces so it reads as a strong blast (user 2026-11-18)."""
    import fxkit as fk
    cx = cy = size / 2
    rng = random.Random(seed)
    n_cr = 8 + 2 * tier
    crowns = [(k * math.tau / n_cr + rng.uniform(-0.08, 0.08), rng.uniform(0.85, 1.15)) for k in range(n_cr)]
    inner = [(k * math.tau / (n_cr // 2) + 0.3, rng.uniform(0.8, 1.1)) for k in range(n_cr // 2)]
    motes = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(14 + 3 * tier)]
    flings = [(rng.uniform(0, math.tau), rng.uniform(0.8, 1.25)) for _ in range(16 + 4 * tier)]
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.45, 0.9)) for _ in range(6 + tier)]
    cl = 5 + tier * 1.6          # crystal length
    cw = 2 + tier * 0.35         # crystal half width
    radius = min(radius, size / 2 - cl * 0.7 - 6)   # the ring and its crystals stay inside the frame
    out = []

    def crown(c, r, scale, solid=True):
        lay = fk.layer(size)
        for a, k in crowns:
            fk.crystal(lay, cx + math.cos(a) * r, cy + math.sin(a) * r, a, cl * k * scale, cw * scale, ICE, ICE_M, ICE_D, CORE)
        if tier >= 3:
            for a, k in inner:
                fk.crystal(lay, cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, a, cl * 0.7 * k * scale,
                           cw * 0.8 * scale, ICE, ICE_M, DEEP, CORE)
        fk.stack(c, lay, OUT if solid else None)

    for f in range(16):
        c = Canvas(size, size)
        if f < 4:   # gather: motes stream in, the core charges
            t = (f + 1) / 4
            for a, d in motes:
                r = radius * d * (1.05 - 0.8 * t)
                aa = a + t * 1.8
                x, y = cx + math.cos(aa) * r, cy + math.sin(aa) * r
                fk.streak(c, x, y, -math.sin(aa), math.cos(aa), 3 + tier * 0.5, CORE, ICE_M)
            fk.glow(c, cx, cy, 4 + 6 * t + tier, [DEEP, ICE_D, ICE_M, ICE, CORE])
            if f == 3:
                fk.sparkle(c, int(cx), int(cy), 4 + tier, CORE, ICE)
        elif f == 4:   # flash
            fk.glow(c, cx, cy, radius * 0.55, [ICE_M, ICE, CORE], density=0.9)
            fk.rays(c, cx, cy, radius * 0.4, radius * 1.05, 12 + 2 * tier, ICE, CORE, rot=0.1, width=2)
            fk.sparkle(c, int(cx), int(cy), 7 + tier, CORE, CORE)
        elif f < 8:    # burst: shock ring, crystals ride it, snow flung out
            t = (f - 4) / 3
            rr = radius * (0.55 + 0.45 * t)
            fk.glow(c, cx, cy, rr * 0.95, [ICE_D, ICE_M], density=0.14 - 0.05 * t)
            fk.rays(c, cx, cy, rr * 0.2, rr * 0.8, 10 + tier, ICE_M, None, rot=0.25 * f)
            fk.ring_band(c, cx, cy, rr + 2, [OUT, ICE_D, ICE_M, ICE, CORE])
            crown(c, rr * 0.82, 0.7 + 0.3 * t)
            for a, d in flings:
                r = rr * d + t * 6
                fk.streak(c, cx + math.cos(a) * r, cy + math.sin(a) * r, math.cos(a), math.sin(a), 4, CORE, ICE)
            if tier >= 5:
                _snowflake(c, cx, cy, rr * 0.35, f * 0.2, CORE, CORE)
        elif f < 12:   # the crystal crown stands, frost cracks glint
            rr = radius * 0.92
            fk.glow(c, cx, cy, rr, [ICE_D, ICE_M], density=0.06)
            for a, d in cracks:
                x1, y1 = cx + math.cos(a) * rr * d, cy + math.sin(a) * rr * d
                c.line(int(cx), int(cy), int(x1), int(y1), ICE_D, 2)
                c.line(int(cx), int(cy), int(x1), int(y1), ICE_M)
            if tier >= 4:   # rune circle
                fk.ring_band(c, cx, cy, rr * 0.5, [ICE_D, ICE_M])
                for k in range(6):
                    a = k * math.pi / 3 + f * 0.05
                    fk.sparkle(c, int(cx + math.cos(a) * rr * 0.5), int(cy + math.sin(a) * rr * 0.5), 2, CORE, ICE_M)
            crown(c, rr * 0.82, 1.0)
            if tier >= 5:
                lay = fk.layer(size)
                fk.crystal(lay, cx, cy + 6, -math.pi / 2, 14 + tier * 2, 5, ICE, ICE_M, ICE_D, CORE)
                fk.crystal(lay, cx - 4, cy + 6, -math.pi / 2 - 0.4, 10, 3, ICE, ICE_M, DEEP, CORE)
                fk.crystal(lay, cx + 4, cy + 6, -math.pi / 2 + 0.4, 10, 3, ICE, ICE_M, DEEP, CORE)
                fk.stack(c, lay, OUT)
            for k in range(5 + tier):   # twinkles
                a = k * 2.399 + f * 0.7
                d = 0.25 + (k * 0.137 % 0.6)
                if (k + f) % 3 == 0:
                    fk.sparkle(c, int(cx + math.cos(a) * rr * d), int(cy + math.sin(a) * rr * d), 2, CORE, ICE)
        else:          # shatter: shards fly out, everything thins away
            k2 = f - 11
            rr = radius * 0.92
            crown(c, rr * (0.82 + 0.06 * k2), max(0.3, 1.0 - 0.2 * k2), solid=k2 < 3)
            for a, d in flings:   # broken shards fly out with trails
                r = rr * (0.75 + 0.1 * k2) * d
                fk.streak(c, cx + math.cos(a) * r, cy + math.sin(a) * r - k2 * 2, math.cos(a), math.sin(a), 5, CORE, ICE)
            _fade(c, min(0.9, 0.05 + 0.2 * k2))
        out.append(c)
    return out


# --- blizzard ---------------------------------------------------------------------

BLIZZ_MS = [80, 80, 80, 80] + [70] * 10 + [100, 100, 110, 130]


def blizzard(tier, size, radius, seed=7):
    """18 frames of a blizzard vortex on a size x size frame (radius = hit radius)."""
    cx = cy = size / 2
    rng = random.Random(seed)
    arms = 2 + tier // 2
    flakes = [(rng.uniform(0.15, 1.0), rng.uniform(0, math.tau), rng.choice([SNOW, ICE, CORE])) for _ in range(20 + 6 * tier)]
    out = []
    for f in range(18):
        c = Canvas(size, size)
        grow = min(1.0, (f + 1) / 4)
        rot = f * 0.38
        scatter = max(0, f - 13) / 4.0
        rr = radius * (0.35 + 0.65 * grow) * (1 + 0.25 * scatter)
        _disk(c, cx, cy, rr, NIGHT, density=0.18 * (1 - scatter))
        _ring(c, cx, cy, rr, DEEP)
        for a_i in range(arms):   # spiral arms
            base = rot + a_i * math.tau / arms
            prev = None
            steps = 26
            for s in range(steps + 1):
                u = s / steps
                r = rr * (0.12 + 0.86 * u)
                a = base + u * 2.6
                pt = (int(round(cx + math.cos(a) * r)), int(round(cy + math.sin(a) * r)))
                if prev:
                    c.line(prev[0], prev[1], pt[0], pt[1], SNOW if u > 0.5 else ICE_M, 2 if u < 0.7 else 1)
                prev = pt
        for r_u, a0, col in flakes:   # orbiting flakes, faster near the eye
            a = a0 + rot * (1.6 - r_u)
            r = rr * r_u * (1 + scatter * 0.8)
            _p(c, cx + math.cos(a) * r, cy + math.sin(a) * r, col)
        if tier >= 3:   # orbiting ice shards
            for k in range(tier):
                a = -rot * 1.3 + k * math.tau / tier
                _shard(c, cx, cy, a, rr * 0.6, 3 + tier * 0.5, ICE, CORE)
        _disk(c, cx, cy, 2 + tier * 0.5, ICE_M)
        _disk(c, cx, cy, 1 + tier * 0.3, CORE)
        if f >= 14:
            _fade(c, min(0.95, 0.15 + 0.22 * (f - 13)))
        out.append(c)
    return out
