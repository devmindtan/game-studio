"""itemprocfx: one-shot visuals for legendary item specials that had none.

Hero-sized 48x48, feet anchor (24,44). Four kinds (user 2026-11-20):
  heal    Huyết quyền - a green/gold cross swells and sends life motes up
  revive  Tim bất diệt - a heart bursts into light, then scatters
  reset   Vĩnh cửu - a clock dial spins, a bright hand sweeps, sparks fly
  haste   Lưu tinh - golden comet streaks wrap the hero and lift off
12 frames each, loop=false, animation name "cast".
"""
from __future__ import annotations

import math

from heroaura import ANCHOR, canvas, px

TAU = math.tau
CX, CY = 24.0, 30.0

PAL = {
    "heal": {"o": "#1d5a3a", "g": "#6fe08a", "w": "#d8ffe4", "s": "#ffe9a8"},
    "revive": {"o": "#7a2a4a", "p": "#ff8ac0", "w": "#fff0f8", "s": "#ffe9a8"},
    "reset": {"o": "#2a2a6a", "b": "#8fd8ff", "w": "#ffffff", "s": "#ffe9a8"},
    "haste": {"o": "#7a4a12", "y": "#ffd96a", "w": "#fff8e0", "s": "#9fdcff"},
}


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _heal(c, i, p):
    t = i / 11
    r = 4 + 9 * math.sin(math.pi * min(1.0, t * 1.4))
    for dy in range(-int(r), int(r) + 1):
        for dx in range(-int(r), int(r) + 1):
            d = abs(dx) + abs(dy)
            if d > r:
                continue
            col = p["o"] if d > r - 2 else (p["w"] if d < 3 else p["g"])
            if (abs(dx) < 3 or abs(dy) < 3) and _h01(dx, dy, i) < 0.85:
                px(c, CX + dx, CY + dy, col)
    for k in range(6):
        a = k * TAU / 6 + i * 0.2
        x = CX + math.cos(a) * (8 + 8 * t)
        y = CY + math.sin(a) * (5 + 5 * t) - 12 * t
        px(c, x, y, p["s"] if k % 2 else p["w"])


def _heart(x, y, r):
    pts = []
    for s in range(40):
        a = s * TAU / 40
        hx = 16 * math.sin(a) ** 3
        hy = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((x + hx * r / 16, y - hy * r / 16))
    return pts


def _revive(c, i, p):
    t = i / 11
    r = 3 + 11 * math.sin(math.pi * min(1.0, t * 1.25))
    for x, y in _heart(CX, CY - 2, r):
        px(c, x, y, p["o"])
    for x, y in _heart(CX, CY - 2, max(1, r - 1.5)):
        px(c, x, y, p["p"] if _h01(x, y, i) < 0.85 else p["w"])
    if i < 7:
        for k in range(12):
            a = k * TAU / 12
            d = 8 + t * 16
            px(c, CX + math.cos(a) * d, CY + math.sin(a) * d * 0.7,
               p["w"] if k % 3 else p["s"])
    for k in range(5):
        a = k * TAU / 5 + i * 0.35
        px(c, CX + math.cos(a) * (6 + 10 * t), CY - 14 - 8 * t + math.sin(a) * 3, p["s"])


def _reset(c, i, p):
    t = i / 11
    r = 13
    for k in range(48):
        a = k * TAU / 48 + i * 0.26
        x, y = CX + math.cos(a) * r, CY + math.sin(a) * r * 0.85
        px(c, x, y, p["o"] if k % 4 else p["b"])
    for k in range(12):
        a = k * TAU / 12 + i * 0.26
        rr = r - 3 if k % 3 else r - 5
        px(c, CX + math.cos(a) * rr, CY + math.sin(a) * rr * 0.85, p["s"])
    a = i * TAU / 11
    for s in range(0, r - 3):
        px(c, CX + math.cos(a) * s, CY + math.sin(a) * s * 0.85, p["w"])
    px(c, CX, CY, p["w"])
    for k in range(4):
        ang = k * TAU / 4 - i * 0.5
        d = 16 + 6 * t
        px(c, CX + math.cos(ang) * d, CY + math.sin(ang) * d * 0.7, p["s"])


def _haste(c, i, p):
    t = i / 11
    for k in range(4):
        a = k * TAU / 4 + i * 0.30
        for s in range(9):
            rr = 6 + s + 10 * t
            x = CX + math.cos(a + s * 0.09) * rr
            y = CY + math.sin(a + s * 0.09) * rr * 0.55 - 6 * t
            if _h01(x, y, k + i) < 0.3:
                continue
            px(c, x, y, p["o"] if s > 6 else (p["w"] if s < 3 else p["y"]))
    for k in range(5):
        a = k * TAU / 5 + i * 0.4
        px(c, CX + math.cos(a) * (5 + 9 * t), CY - 9 - 8 * t, p["s"])


DRAW = {"heal": _heal, "revive": _revive, "reset": _reset, "haste": _haste}


def frame(kind, i):
    c = canvas()
    DRAW[kind](c, i, PAL[kind])
    return c


def build(here, name, kind, export):
    export(here, name, [("cast", [frame(kind, i) for i in range(12)], 15, False, {})],
           anchor=ANCHOR)
