"""fxkit: drawing pieces for strong-looking pixel effects (user 2026-11-18: effects looked
too simple, they must show the skill's power).

Pieces: faceted crystals (lit face, shaded face, white edge, dark outline), light rays,
4-point sparkles, streaked particles, banded glow disks, and layers outlined on their
own before they are stacked (so shapes stay readable over busy fights).
"""

from __future__ import annotations

import math

from spritekit import Canvas
from icefx import BAYER, _p


def layer(size_w, size_h=None):
    return Canvas(size_w, size_h or size_w)


def stack(base, top, outline=None):
    """top (optionally outlined first) composited over base."""
    if outline:
        top.outline(outline)
    base.img.alpha_composite(top.img)
    return base


def glow(c, cx, cy, r, bands, density=1.0):
    """Banded radial glow: bands = colours from the rim inward."""
    n = len(bands)
    for k, col in enumerate(bands):
        rr = r * (1 - k / n)
        ri = int(math.ceil(rr))
        for y in range(-ri, ri + 1):
            for x in range(-ri, ri + 1):
                if x * x + y * y <= rr * rr:
                    px, py = int(cx + x), int(cy + y)
                    if BAYER[py % 4][px % 4] < density * 16:
                        _p(c, px, py, col)


def rays(c, cx, cy, r0, r1, n, col, tip=None, rot=0.0, width=1):
    for k in range(n):
        a = rot + k * math.tau / n
        long = r1 if k % 2 == 0 else r0 + (r1 - r0) * 0.6
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        x1, y1 = cx + math.cos(a) * long, cy + math.sin(a) * long
        c.line(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), col, width)
        if tip:
            _p(c, x1, y1, tip)


def sparkle(c, x, y, r, core, arm):
    """4-point star: a bright core and two crossing arms."""
    for k in range(1, r + 1):
        col = arm if k > 1 else core
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            _p(c, x + dx, y + dy, col)
    _p(c, x, y, core)


def streak(c, x, y, dx, dy, length, head, tail):
    """A particle with a motion trail along (dx, dy)."""
    n = max(1, int(length))
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    for k in range(n):
        _p(c, x - ux * k, y - uy * k, head if k == 0 else tail)


def crystal(c, x, y, angle, length, width, lit, mid, dark, edge):
    """A faceted shard from (x, y) pointing along angle: the left face lit, the right
    shaded, a bright ridge down the middle."""
    ux, uy = math.cos(angle), math.sin(angle)
    px, py = -uy, ux
    tip = (x + ux * length, y + uy * length)
    l = (x + px * width, y + py * width)
    r = (x - px * width, y - py * width)
    mid_pt = (x + ux * length * 0.15, y + uy * length * 0.15)
    rnd = lambda q: (int(round(q[0])), int(round(q[1])))
    c.polygon([rnd(l), rnd(tip), rnd(mid_pt)], lit)
    c.polygon([rnd(r), rnd(tip), rnd(mid_pt)], dark)
    c.line(*rnd(mid_pt), *rnd(tip), mid)
    c.line(*rnd(((mid_pt[0] + tip[0]) / 2, (mid_pt[1] + tip[1]) / 2)), *rnd(tip), edge)


def ring_band(c, cx, cy, r, cols):
    """A thick ring: cols from outside in, one px each."""
    for k, col in enumerate(cols):
        rr = r - k
        if rr > 0:
            c.ellipse(int(cx - rr), int(cy - rr), int(cx + rr), int(cy + rr), col, fill=False)
