"""hitfx: options for the hit spark of physical melee hits (bach-ai roadmap "cảm giác đánh", 2026-11-23).
48 px canvas at double density (px_scale 0.5 -> 24 px, x2 sprite_scale -> 48 px on screen). Anchor = the
hit point (centre). Short: 5 frames at 20 fps. Solid pixels, dark rim, no dither.

Reference: action games of the genre (Hades, Dead Cells, Brotato) mark a melee hit with a bright white
centre and a few hard shards for 2-4 frames; the colour stays neutral (white / pale gold) so element
colours keep their meaning.
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
from icefx import _p
from elementfx import _disk, _ring, _rim, _star4

S = 48
C = S // 2
W = "#ffffff"
Y1 = "#fff3c4"
Y2 = "#ffd36a"
O = "#f08a2c"
X = "#2a1606"


def spark_star(frames=5):
    """A: a white four-point star that snaps open and shrinks, with two tiny glints."""
    out = []
    for f, r in enumerate((7, 12, 10, 6, 3)[:frames]):
        c = Canvas(S, S)
        _star4(c, C, C, r, W, Y1 if f < 2 else Y2, Y2 if f < 3 else O)
        if 1 <= f <= 3:
            for gx, gy in ((C + 9, C - 8), (C - 8, C + 7)):
                _p(c, gx, gy, W)
        _rim(c, X)
        out.append(c)
    return out


def spark_shards(frames=5):
    """B: a white flash and six hard shards flying out, cooling from white to orange."""
    rng = random.Random(7)
    dirs = [(a + rng.uniform(-0.25, 0.25)) for a in [i * math.tau / 6 for i in range(6)]]
    out = []
    for f in range(frames):
        c = Canvas(S, S)
        if f < 2:
            _disk(c, C, C, 4.5 - f * 2, W)
        for k, a in enumerate(dirs if f > 0 else []):   # frame 0: the flash alone
            d0 = 3 + f * 3.5
            ln = max(1, 5 - f)
            col = (W, Y1, Y2, O, O)[f]
            for t in range(ln):
                _p(c, C + math.cos(a) * (d0 + t), C + math.sin(a) * (d0 + t), col)
        _rim(c, X)
        out.append(c)
    return out


def spark_ring(frames=5):
    """C: an X of two slashes over a quick widening ring."""
    out = []
    for f in range(frames):
        c = Canvas(S, S)
        r = 3 + f * 3
        if f < 4:
            _ring(c, C, C, r, Y1 if f < 2 else Y2, 2.0 if f < 2 else 1.0)
        if f < 3:
            ln = (6, 11, 8)[f]
            for t in range(-ln, ln + 1):   # an X of two slashes: not a ring with one bar ("no entry")
                for sx in (1, -1):
                    _p(c, C + t, C - t * sx, W)
                    if abs(t) < ln - 2:
                        _p(c, C + t + 1, C - t * sx, Y1)
        _rim(c, X)
        out.append(c)
    return out
