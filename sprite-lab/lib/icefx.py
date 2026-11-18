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

FROST_MS = [70, 70, 70, 70, 55, 55, 55, 55, 110, 110, 110, 110, 90, 90, 100, 120]


def frost_nova(tier, size, radius, seed=1):
    """16 frames of a frost nova on a size x size frame; radius = the hit radius (px)."""
    cx = cy = size / 2
    rng = random.Random(seed)
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.5, 0.95)) for _ in range(5 + tier * 2)]
    n_shards = 10 + 2 * tier
    spikes = 6 + tier
    out = []
    for f in range(16):
        c = Canvas(size, size)
        if f < 4:   # gather: motes spiral in, the core grows
            t = (f + 1) / 4
            for k in range(8 + 2 * tier):
                a = k * math.tau / (8 + 2 * tier) + t * 1.6
                r = radius * 0.9 * (1 - t * 0.75)
                _p(c, cx + math.cos(a) * r, cy + math.sin(a) * r, ICE if k % 2 else SNOW)
                _p(c, cx + math.cos(a - 0.12) * (r + 2), cy + math.sin(a - 0.12) * (r + 2), ICE_M)
            _disk(c, cx, cy, 2 + 4 * t + tier * 0.6, ICE_M)
            _disk(c, cx, cy, 1 + 2.5 * t + tier * 0.4, CORE)
        elif f < 8:  # burst: the ring runs out, shards ride it
            t = (f - 3) / 4
            rr = radius * (0.35 + 0.65 * t)
            _disk(c, cx, cy, rr * 0.9, FROST, density=0.12 + 0.12 * (1 - t))
            _disk(c, cx, cy, max(1.5, (1 - t) * 7), CORE)
            if tier >= 2:   # petals
                for k in range(6):
                    a = k * math.pi / 3 + 0.3
                    _shard(c, cx, cy, a, rr * 0.2, rr * 0.22, ICE_M, CORE)
            _ring(c, cx, cy, rr, DEEP, 2)
            _ring(c, cx, cy, rr - 2, ICE_D)
            _ring(c, cx, cy, rr - 3, ICE_M)
            for k in range(n_shards):
                a = k * math.tau / n_shards + (0.08 if f % 2 else -0.08)
                _shard(c, cx, cy, a, rr - 1, 3 + tier * 0.6, ICE if k % 2 else SNOW, CORE)
        else:        # frozen ground lingers, then shatters
            phase = f - 8
            fading = max(0, phase - 3) / 4.0 if f >= 12 else 0.0
            rr = radius * 0.95
            _disk(c, cx, cy, rr * 0.7, FROST, density=0.08)   # a light frost, not a carpet (user 2026-11-18)
            _ring(c, cx, cy, rr, ICE_D)
            for a, length in cracks:
                c.line(int(cx), int(cy), int(round(cx + math.cos(a) * rr * length)),
                       int(round(cy + math.sin(a) * rr * length)), DEEP)
            if tier >= 4:   # runes on the floor
                pts = [(cx + math.cos(k * math.pi / 3) * rr * 0.55, cy + math.sin(k * math.pi / 3) * rr * 0.55) for k in range(7)]
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    c.line(int(x0), int(y0), int(x1), int(y1), ICE_M)
            if tier >= 5:
                _snowflake(c, cx, cy, rr * 0.4, 0.2 + f * 0.05, ICE_M, CORE)
            if f < 12:
                if tier >= 3:   # standing spikes round the edge
                    for k in range(spikes):
                        a = k * math.tau / spikes
                        _spike(c, cx + math.cos(a) * rr * 0.82, cy + math.sin(a) * rr * 0.82, 5 + tier, 2)
                for k in range(6):   # shimmer
                    a = (k * 1.7 + f * 0.9) % math.tau
                    _p(c, cx + math.cos(a) * rr * (0.3 + 0.1 * k), cy + math.sin(a) * rr * (0.3 + 0.1 * k), CORE)
            else:   # shatter: flakes fly out and up
                k2 = f - 11
                for k in range(n_shards):
                    a = k * math.tau / n_shards + 0.2
                    r = rr * 0.82 + k2 * 4
                    _p(c, cx + math.cos(a) * r, cy + math.sin(a) * r - k2 * 3, SNOW if k % 2 else ICE)
                    _p(c, cx + math.cos(a) * r + 1, cy + math.sin(a) * r - k2 * 3, ICE_M)
                _fade(c, min(0.95, 0.2 + 0.22 * k2))
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
