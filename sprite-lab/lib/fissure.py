"""fissure: the Earth Strike family seen from above (Bach Ai is a top-down arena).

One impact point; fault lines run out of it OFF-AXIS (earth DNA: uneven, heavy,
never the symmetric rings of the frost family), rock slabs heave up along them on
the damage frames, magma shows in the cracks on higher tiers, then everything
cools and crumbles. Tier I (earth-strike-i/gen.py) is the single fault line this
family grows from; II-V call `frames(spec)` with more arms, rocks and magma.

8 frames, 14 fps, one shot: 0 impact · 1-2 cracks run · 2-5 rocks up (hitbox
active 2..6) · 6 rocks crack · 7 dust and cooled cracks.
Faint dust (alpha < 96) does not count for the hitbox (spritekit.fit_hitbox).
"""
from __future__ import annotations

import math
import random

from spritekit import Canvas

ROCK = "#8a6a52"; ROCK_L = "#c79a6a"; ROCK_D = "#5a4335"; STRATA = "#6e503c"
CRACK = "#2b2028"; SHADOW = "#1e161c"; DUST = "#c9a882"; SAND = "#a9815c"
MAGMA = "#ff6a2a"; MAGMA_D = "#b8331a"; GLOW = "#ffd08a"; ASH = "#6b5a52"
F_DUST = "#c9a88250"; F_SAND = "#a9815c48"

REACH = [0.0, 0.4, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0]     # how far the cracks have run, per frame


def _arm_points(cx, cy, angle_deg, length, seed):
    """A jagged fault line: steps out along the angle, kinking sideways."""
    rng = random.Random(seed)
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    steps = max(3, int(length / 5))
    pts = [(cx, cy)]
    side = 1 if rng.random() < 0.5 else -1
    for k in range(1, steps + 1):
        r = length * k / steps
        off = side * rng.choice((1, 2, 2, 3)) * (0.4 if k == 1 else 1.0)
        side = -side if rng.random() < 0.7 else side
        pts.append((cx + ux * r + px * off, cy + uy * r + py * off))
    return pts


def _cut(pts, frac):
    """The part of a polyline that has run so far."""
    if frac >= 1:
        return pts
    n = max(2, int(round(1 + (len(pts) - 1) * frac)))
    return pts[:n]


def _slab(c, x, y, s, phase, seed):
    """A rock slab heaving out of the ground, seen from above: shadow, sides, lit top.
    phase 0 small, 1 full, 2 cracked, 3 crumbs."""
    rng = random.Random(seed)
    if phase == 3:
        for k in range(3):
            c.pixel(int(x + rng.randint(-s, s)), int(y + rng.randint(-s, s)), ROCK_D if k else STRATA)
        return
    k = 0.55 if phase == 0 else 1.0
    r = max(1.0, s * k)
    tilt = rng.uniform(-0.6, 0.6)
    pts = [(x + math.cos(tilt + i * math.pi / 2) * r * (1.0 if i % 2 else 0.75),
            y + math.sin(tilt + i * math.pi / 2) * r * (1.0 if i % 2 else 0.75)) for i in range(4)]
    c.polygon([(int(round(a + 1)), int(round(b + 2))) for a, b in pts], SHADOW)        # cast shadow
    c.polygon([(int(round(a)), int(round(b + 1))) for a, b in pts], ROCK_D)             # sides
    c.polygon([(int(round(a)), int(round(b))) for a, b in pts], ROCK)                   # body
    top = [(x + (a - x) * 0.55 - 0.5, y + (b - y) * 0.55 - 1) for a, b in pts]
    c.polygon([(int(round(a)), int(round(b))) for a, b in top], ROCK_L)                 # lit top face
    if phase == 2:                                                                       # cracked
        c.line(int(x - r * 0.6), int(y - 1), int(x + r * 0.5), int(y + r * 0.4), CRACK, 1)


def frames(spec):
    """All 8 frames of one tier. spec: size, arms [(angle, length 0..1)], branches
    [(arm index, at 0..1, angle offset, length 0..1)], rocks [(arm, at 0..1, size)],
    magma 0..3 (none, centre, cracks, centre pool + glowing cracks), embers, seed."""
    size = spec["size"]
    cx = cy = size // 2
    R = size / 2 - 4
    seed = spec.get("seed", 7)
    arms = [_arm_points(cx, cy, a, R * l, seed + i) for i, (a, l) in enumerate(spec["arms"])]
    branches = []
    for j, (ai, at, da, l) in enumerate(spec.get("branches", [])):
        base = arms[ai][max(1, int(round((len(arms[ai]) - 1) * at)))]
        ang = spec["arms"][ai][0] + da
        branches.append((at, _arm_points(base[0], base[1], ang, R * l, seed + 50 + j)))
    rocks = []
    for k, (ai, at, s) in enumerate(spec.get("rocks", [])):
        pts = arms[ai]
        x, y = pts[max(1, int(round((len(pts) - 1) * at)))]
        rocks.append((x, y, s, at, seed + 100 + k))
    magma = spec.get("magma", 0)
    out = []
    for i in range(8):
        c = Canvas(size, size)
        reach = REACH[i]
        # faint dust ring rolling out from the impact (not part of the hitbox)
        if 1 <= i <= 7:
            rr = R * (0.45 + 0.09 * i)
            for k in range(14 + size // 8):
                a = k * 2 * math.pi / (14 + size // 8) + i * 0.3
                c.pixel(int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr * 0.9), F_DUST if k % 2 else F_SAND)
        if i == 0:   # impact: a dark pit with a hot point
            c.ellipse(cx - 3, cy - 2, cx + 3, cy + 3, CRACK)
            c.pixel(cx, cy, GLOW)
            out.append(c)
            continue
        hot = MAGMA if i <= 5 else (MAGMA_D if i == 6 else ASH)
        lines = [_cut(p, reach) for p in arms] + [_cut(p, max(0.0, (reach - at) / (1 - at + 1e-6))) for at, p in branches]
        for n, pts in enumerate(lines):
            main = n < len(arms)
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                w = 3 if main else 2
                c.line(int(round(x1 + 1)), int(round(y1 + 1)), int(round(x2 + 1)), int(round(y2 + 1)), ROCK_L if i < 6 else STRATA, 1)
                c.line(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)), CRACK, w)
            if magma >= 2 or (magma == 1 and main and 2 <= i <= 4):   # low tiers: a brief glow near the centre
                limit = len(pts) if magma >= 2 else 1
                for (x1, y1), (x2, y2) in list(zip(pts, pts[1:]))[:limit]:
                    c.line(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)), hot, 1)
        # centre: crater, and a magma pool on the top tier
        c.ellipse(cx - 3, cy - 2, cx + 3, cy + 3, CRACK)
        if magma >= 1 and i <= 6:
            c.ellipse(cx - 1 - (magma >= 3), cy - 1, cx + 1 + (magma >= 3), cy + 1 + (magma >= 3), hot)
            if i in (2, 3) or magma >= 3:
                c.pixel(cx, cy, GLOW)
        # rock slabs heave where the crack has reached
        for x, y, s, at, sd in rocks:
            if reach < at or i < 2:
                continue
            phase = 0 if i == 2 else 1 if i <= 5 else 2 if i == 6 else 3
            _slab(c, x, y, s, phase, sd)
        # embers over the top tier
        if spec.get("embers") and 2 <= i <= 6:
            rng = random.Random(seed + i)
            for _ in range(6):
                a = rng.uniform(0, 2 * math.pi)
                r = rng.uniform(0.3, 0.8) * R
                c.pixel(int(cx + math.cos(a) * r), int(cy + math.sin(a) * r - (i - 2)), GLOW if rng.random() < 0.5 else MAGMA)
        out.append(c)
    return out
