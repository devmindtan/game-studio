"""critfx: three options for the Chí mạng hit flash (bach-ai, user 2026-11-26 "thiết kế lại hiệu ứng khi gây chí mạng").

The game's crit was only a bigger orange number with "!" and a short hitstop on elites. Three different shapes drawn on
the struck monster, for the user to pick:
  A  Chém chéo: two white-gold slashes cross in an X, then split into shards flying out.
  B  Vòng nổ đỏ: a red-hot core, a shockwave ring widening, eight sparks on its rim.
  C  Gai nổ: a jagged comic star (yellow, red rim) punches out big and shrinks to a sparkle.
Flat 2D, solid pixels, 1 px dark rim, no dither (design/special-fx-redesign.md §2). 64 px canvas, px_scale 0.5.
"""

from __future__ import annotations

import math

from spritekit import Canvas
from elementfx import _disk, _ring, _rim

W = "#fffdf0"
Y1 = "#ffe98a"
Y2 = "#ffc23a"
O1 = "#ff8a2a"
R1 = "#e8402a"
R2 = "#a01c1c"
X = "#2a0c08"


def crit_a(size=64, frames=7):
    """A: an X of two slashes drawn in, flash, then shards fly out along the arms."""
    out, c0 = [], size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        if u < 0.5:
            grow = min(1.0, (u + 0.17) / 0.4)
            ln = 26 * grow
            wid = 4 if u < 0.34 else 3
            for s in (1, -1):
                c.line(int(c0 - ln), int(c0 - s * ln), int(c0 + ln), int(c0 + s * ln), Y2, wid + 2)
                c.line(int(c0 - ln), int(c0 - s * ln), int(c0 + ln), int(c0 + s * ln), W, wid)
            if u > 0.1:
                _disk(c, c0, c0, 5 - u * 4, W)
        else:
            d = 10 + (u - 0.5) * 2 * 18
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2
                for j, off in enumerate((0, 6)):
                    px, py = c0 + math.cos(a) * (d + off), c0 + math.sin(a) * (d + off)
                    ln = 4 - j
                    c.line(int(px), int(py), int(px + math.cos(a) * ln), int(py + math.sin(a) * ln), Y1 if u < 0.8 else O1, 2)
        _rim(c, X)
        out.append(c)
    return out


def crit_b(size=64, frames=7):
    """B: a red-hot core, a ring widening and thinning, eight sparks riding its rim."""
    out, c0 = [], size / 2
    for f in range(frames):
        c = Canvas(size, size)
        u = f / (frames - 1)
        r = 6 + u * 19
        _ring(c, c0, c0, r, R1 if u < 0.6 else R2, 3.0 - u * 1.8)
        if u < 0.6:
            core = 9 * (1 - u / 0.6) + 2
            _disk(c, c0, c0, core, O1)
            _disk(c, c0, c0, core * 0.6, Y1)
            _disk(c, c0, c0, core * 0.3, W)
        for k in range(8):
            a = k * math.tau / 8 + 0.2
            sr = r + 3
            _disk(c, c0 + math.cos(a) * sr, c0 + math.sin(a) * sr, 1.6 if u < 0.7 else 1.0, Y2)
        _rim(c, X)
        out.append(c)
    return out


def _spike(c, c0, r_out, r_in, n, rot, col):
    pts = []
    for k in range(n * 2):
        a = rot + k * math.pi / n
        r = r_out * (1.0 if k % 4 == 0 else 0.78) if k % 2 == 0 else r_in
        pts.append((int(round(c0 + math.cos(a) * r)), int(round(c0 + math.sin(a) * r))))
    c.polygon(pts, col)


def crit_c(size=64, frames=7):
    """C: a jagged comic star punches out (big on frame 1), holds, then shrinks to a 4-point sparkle."""
    out, c0 = [], size / 2
    scale = [0.75, 1.0, 0.95, 0.85, 0.6, 0.35, 0.18]
    for f in range(frames):
        c = Canvas(size, size)
        s = scale[f]
        if f < 5:
            _spike(c, c0, 28 * s, 13 * s, 10, -math.pi / 2, R1)
            _spike(c, c0, 21 * s, 10 * s, 10, -math.pi / 2, Y2)
            _spike(c, c0, 12 * s, 6 * s, 10, -math.pi / 2, W)
        else:
            ln = int(14 * s + 3)
            c.line(int(c0 - ln), int(c0), int(c0 + ln), int(c0), Y1, 2)
            c.line(int(c0), int(c0 - ln), int(c0), int(c0 + ln), Y1, 2)
            _disk(c, c0, c0, 1.5, W)
        _rim(c, X)
        out.append(c)
    return out
