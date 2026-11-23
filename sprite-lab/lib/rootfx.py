"""rootfx: options for Rễ trói (root snare), Rừng Âm U's event (bach-ai design/region-events-plan.md §4B,
2026-11-23). One root cluster per sprite, 64 px at double density (px_scale 0.5 -> 32 px in game); the game lays
several clusters along the root line. Frames: 0-2 crack glows (telegraph), 3 soil bulges, 4-6 roots burst up,
7-8 hold, 9-10 roots sink. Anchor = ground centre. Solid pixels, dark rim, no dither, no area overlay.
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
from icefx import _p

S = 64
GX, GY = 32, 46          # ground centre (anchor)
CRACK = "#2a1a10"
GLOW = "#9fe07a"
GLOW2 = "#d8ffb0"
SOIL = "#5a3d24"
SOIL2 = "#7a5634"
BARK = "#4a2e1a"
BARK2 = "#6e4626"
BARK3 = "#8f6136"
MOSS = "#5f9a3c"
LEAF = "#7cc24a"
X = "#160d07"


def _rim(c, col=X):
    w, h = c.width, c.height
    px = c.img.load()
    solid = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0}
    for x, y in solid:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in solid:
                _p(c, q[0], q[1], col)


def _crack(c, glow_k):
    """A zigzag crack across the ground, its inside glowing green as glow_k goes 0..1."""
    rng = random.Random(3)
    pts = [(GX - 24, GY + rng.randint(-2, 2))]
    for i in range(1, 9):
        pts.append((GX - 24 + i * 6, GY + rng.randint(-3, 3)))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        c.line(x0, y0, x1, y1, CRACK, 3)
        if glow_k > 0:
            c.line(x0, y0, x1, y1, GLOW2 if glow_k > 0.66 else GLOW, 1)


def _soil(c, k):
    for i, dx in enumerate((-16, -4, 9, 18)):
        r = 2 + k * (3 + i % 2)
        for y in range(-int(r), 1):
            for x in range(-int(r * 1.4), int(r * 1.4) + 1):
                if (x / (r * 1.4)) ** 2 + (y / r) ** 2 <= 1:
                    _p(c, GX + dx + x, GY + y, SOIL2 if y < -r / 2 else SOIL)


def _hook_root(c, x0, h, bend, w0):
    """A tapering root rising from (x0, GY), curving by `bend`, ending in a hook."""
    for t in range(int(h)):
        u = t / max(1, h)
        x = x0 + bend * u * u * 10
        y = GY - t
        w = max(0.6, w0 * (1 - u))
        for s in range(-int(round(w)), int(round(w)) + 1):
            col = BARK3 if s < 0 else (BARK2 if s == 0 else BARK)
            _p(c, x + s, y, col)
        if t % 7 == 3 and u < 0.8:                          # moss and a thorn
            _p(c, x + w + 1, y, MOSS)
            _p(c, x - w - 1, y - 1, BARK3)
    tipx = x0 + bend * 10
    for k in range(4):                                      # the hook
        _p(c, tipx + math.copysign(k, bend), GY - h - (1 if k < 2 else 0) + k // 2, BARK2)


def root_hooks(frames=11):
    """Thorny hooked roots (option A, chosen 2026-11-23 over braided vines and wooden stakes), dark bark with moss, bursting up in a ragged row."""
    out = []
    for f in range(frames):
        c = Canvas(S, S)
        if f <= 2:
            _crack(c, (f + 1) / 3)
        elif f == 3:
            _crack(c, 1.0)
            _soil(c, 1.0)
        else:
            _soil(c, 0.6)
            grow = {4: 0.45, 5: 0.85, 6: 1.1, 7: 1.0, 8: 1.0, 9: 0.6, 10: 0.25}[f]
            for x0, h, bend, w in ((-14, 26, -1, 3.2), (-3, 34, 1, 4.0), (9, 28, 1, 3.4), (18, 20, -1, 2.6)):
                _hook_root(c, GX + x0, h * grow, bend, w)
        _rim(c)
        out.append(c)
    return out
