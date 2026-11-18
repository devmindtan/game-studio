"""orbit_shields: three bucklers on a HORIZONTAL 3D orbit around the hero.

The orbit is a flattened ellipse around the waist (24,30): radius 16 x 5.
Shields on the far half (upper arc) go in a "back" sprite drawn before the
hero; shields on the near half (lower arc) go in a "front" sprite drawn after
him. Both sprites use the same phase, so the three wards travel as one ring
that passes behind and in front of the body (user 2026-11-18).
"""
from __future__ import annotations

import math

from heroaura import ANCHOR, canvas, px

CX, CY, RX, RY = 24.0, 30.0, 18.0, 6.0
TAU = math.tau

OUT = "#7a4a12"
GOLD = "#ffd96a"
RIM = "#fff3c0"
HOT = "#ffffff"


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _buckler(c, x, y, ang, scale, lit):
    ca, sa = math.cos(ang), math.sin(ang)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            wx, wy = x + dx, y + dy
            u = (ca * dx + sa * dy) / scale
            v = (-sa * dx + ca * dy) / scale
            half = 3.2 if u <= 0 else max(1.0, 3.2 - (u - 0.5) * 0.8)
            if abs(u) > 3.4 or abs(v) > half:
                continue
            if abs(u) > 2.7 or abs(v) > half - 0.9:
                px(c, wx, wy, OUT)
            elif abs(u) < 1.0 and abs(v) < 1.0:
                px(c, wx, wy, HOT if lit else RIM)
            else:
                px(c, wx, wy, RIM if v < -0.5 else GOLD)


def frame(side, i, form=1.0):
    """side = 'back' (sin < 0, upper arc) or 'front' (sin >= 0, lower arc)."""
    c = canvas()
    rx, ry = RX * form, RY * form

    # the orbit itself: far half dim, near half bright
    for k in range(160):
        a = k * TAU / 160
        far = math.sin(a) < 0
        if (side == "back") != far:
            continue
        if _h01(k, i // 2, 7) < 0.42:
            continue
        x = CX + math.cos(a) * rx
        y = CY + math.sin(a) * ry
        px(c, x, y, "#ffe9a860" if far else "#fff3c0b0")

    for k in range(3):
        a = k * TAU / 3 + i * TAU / 8
        far = math.sin(a) < 0
        if (side == "back") != far:
            continue
        x = CX + math.cos(a) * rx
        y = CY + math.sin(a) * ry
        scale = 0.75 if far else 1.0
        # a short trail along the ellipse makes the horizontal orbit readable
        for s in (1, 2, 3):
            b = a - s * 0.20
            tx = CX + math.cos(b) * rx
            ty = CY + math.sin(b) * ry
            px(c, tx, ty, RIM if s == 1 else "#ffd96a40")
        _buckler(c, x, y, a, scale, lit=(k == i % 3 and not far))

    if form < 1.0 and side == "front":
        px(c, CX, CY, HOT)
        px(c, CX + 1, CY, RIM)
        px(c, CX - 1, CY, RIM)
    return c


def build(here, name, side, export):
    anims = [("form", [frame(side, 0, f) for f in (0.55, 0.80, 0.95, 1.10)], 16, False, {}),
             ("loop", [frame(side, i) for i in range(8)], 10, True, {})]
    export(here, name, anims, anchor=ANCHOR)
