"""arrowfx: the Cung thủ's arrow drawn straight at each flight angle (no image rotation: stays crisp), double
density (px_scale 0.5), head at the canvas centre (anchor = hit point). Three looks to choose (2026-11-23):
  A wood: brown shaft, grey steel head, white fletching.
  B steel: pale steel shaft and head, a short white streak behind.
  C wind: green fletching with two wind lines trailing.
"""

from __future__ import annotations

import math

from spritekit import Canvas
from icefx import _p
from elementfx import _rim

X = "#1b1208"


def _along(c, cx, cy, ux, uy, d0, d1, col, w=1):
    """Line from d0 to d1 px behind the head (negative = ahead) along -u, width w (perpendicular)."""
    n = int(abs(d1 - d0)) + 1
    for k in range(n):
        d = d0 + (d1 - d0) * k / max(1, n - 1)
        x, y = cx - ux * d, cy - uy * d
        for s in range(-(w // 2), w - w // 2):
            _p(c, x - uy * s, y + ux * s, col)


def arrow(style: str, size: int, deg: float, frames: int = 4):
    out = []
    ux, uy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    cx = cy = size / 2
    for f in range(frames):
        c = Canvas(size, size)
        if style == "b":                                  # streak first (under)
            _along(c, cx, cy, ux, uy, 18, 30 + (f % 2) * 3, "#ffffff", 1)
        if style == "c":
            for side in (-3, 3):
                _along(c, cx - uy * side, cy + ux * side, ux, uy, 16 + f, 24 + f * 2, "#bdf0c8", 1)
        shaft = {"a": "#a8743e", "b": "#d8e0ea", "c": "#a8743e"}[style]
        _along(c, cx, cy, ux, uy, 2, 20, shaft, 2)
        head = {"a": "#c0c8d0", "b": "#ffffff", "c": "#c0c8d0"}[style]
        for k in range(5):                                 # arrowhead: a small triangle
            wid = (0, 1, 1, 2, 2)[k]          # pointed tip, barbs behind
            for s in range(-wid, wid + 1):
                _p(c, cx - ux * k - uy * s * 0.9, cy - uy * k + ux * s * 0.9, head)
        fl = {"a": "#f0ece0", "b": "#a8b4c4", "c": "#4fb86a"}[style]
        for k in range(4):                                 # fletching at the tail, two vanes
            for s in (-2 - k // 2, 2 + k // 2):
                _p(c, cx - ux * (17 + k) - uy * s * 0.8, cy - uy * (17 + k) + ux * s * 0.8, fl)
        _rim(c, X)
        out.append(c)
    return out
