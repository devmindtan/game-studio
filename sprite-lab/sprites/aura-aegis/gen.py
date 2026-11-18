#!/usr/bin/env python3
"""aura-aegis — Thần hộ: three small golden shields orbiting the hero's torso.

User 2026-11-18: it was a single bubble with turning runes, too close to the
magnetic shield. Now there is no enclosing bubble: three bucklers circle a
point at mid-body (24,30), leaving the hero fully visible. Each has a short
motion trail, and a faint dotted orbit shows the path. Same 48x48 frame and
feet anchor (24,44), same 4 form + 8 loop frames and "loop" name the game uses.
"""
import math
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from heroaura import canvas, px, ANCHOR  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name

CX, CY, R = 24.0, 30.0, 15.0          # orbit centre = the hero's waist
OUT = "#7a4a12"                      # dark gold edge
GOLD = "#ffd96a"                     # buckler body
RIM = "#fff3c0"                      # bright edge
HOT = "#ffffff"
ORBIT = "#ffe9a840"                  # faint dotted orbit
TAU = math.tau


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _buckler(c, x, y, ang, hot):
    """A small golden shield facing out along [ang], with a white rune."""
    ca, sa = math.cos(ang), math.sin(ang)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            wx, wy = x + dx, y + dy
            u = ca * dx + sa * dy
            v = -sa * dx + ca * dy
            half = 3.2 if u <= 0 else max(1.0, 3.2 - (u - 0.5) * 0.8)
            if abs(u) > 3.4 or abs(v) > half:
                continue
            if abs(u) > 2.7 or abs(v) > half - 0.9:
                px(c, wx, wy, OUT)
            elif abs(u) < 1.0 and abs(v) < 1.0:
                px(c, wx, wy, HOT if hot else RIM)
            else:
                px(c, wx, wy, RIM if v < -0.5 else GOLD)


def _orbit(c, i):
    """A broken golden circle shows where the three shields travel."""
    for k in range(90):
        a = k * TAU / 90
        if _h01(k, i // 2, 7) < 0.45:
            continue
        px(c, CX + math.cos(a) * R, CY + math.sin(a) * R * 0.95, ORBIT)


def frame(i, form=1.0):
    c = canvas()
    radius = R * form
    _orbit(c, i) if form >= 1.0 else None
    for k in range(3):
        a = k * TAU / 3 + i * TAU / 8
        x = CX + math.cos(a) * radius
        y = CY + math.sin(a) * radius * 0.95
        # a short trail along the orbit makes the rotation readable at 10 fps
        for s in range(1, 4):
            b = a - s * 0.22
            tx = CX + math.cos(b) * radius
            ty = CY + math.sin(b) * radius * 0.95
            px(c, tx, ty, RIM if s == 1 else ORBIT)
        _buckler(c, x, y, a, hot=(k == i % 3))
    if form < 1.0:
        # the three wards arrive from outside and flash once as they lock in
        px(c, CX, CY, HOT)
        px(c, CX + 1, CY, RIM)
        px(c, CX - 1, CY, RIM)
        px(c, CX, CY + 1, RIM)
    return c


ANIM = [("form", [frame(0, f) for f in (0.55, 0.80, 0.95, 1.10)], 16, False, {}),
        ("loop", [frame(i) for i in range(8)], 10, True, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
