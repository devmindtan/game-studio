#!/usr/bin/env python3
"""stone-ward-break — Bàn thạch vỡ ngay khi chặn được một đòn.

One-shot, 6 frames / 18 fps: the cracks light up, the stone shell splits, then
six chunks fly outward and crumble into dust. Drawn at the hero's own frame and
feet anchor (24,44) so the game can spawn it where the ward was.
User 2026-11-18.
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
from spritekit import Canvas  # noqa: E402
from heroaura import ellipse_points  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W = H = 48
ANCHOR = (24.0, 44.0)
CX, CY = 24.0, 27.0
TAU = math.tau

OUT = "#3a2a18"
STONE = "#8a8070"
LIT = "#ffb04a"
HOT = "#fff0b4"


def px(c, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        c.pixel(x, y, col)


def _shell(c, broken):
    for (x, y), a in ellipse_points(CX, CY, 21, 17, 240):
        if broken and int(a * 5) % 3 == 0:
            continue
        px(c, x, y, OUT)
    for (x, y), a in ellipse_points(CX, CY, 20, 16, 240):
        if broken and int(a * 5) % 3 == 0:
            continue
        px(c, x, y, LIT if broken else STONE)


def _cracks(c, hot):
    for k in range(4):
        a = k * TAU / 4 + 0.3
        for s in range(3, 9):
            x = CX + math.cos(a) * (20 - s)
            y = CY + math.sin(a) * (16 - s * 0.8)
            px(c, x, y, HOT if hot else LIT)


def _chunk(c, x, y, fade):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if abs(dx) + abs(dy) > 1:
                continue
            px(c, x + dx, y + dy, OUT)
    if not fade:
        px(c, x, y, HOT if (int(x + y) % 2) else LIT)


def frame(i):
    c = Canvas(W, H)
    if i == 0:                       # every crack flares at once
        _shell(c, False)
        _cracks(c, True)
        px(c, CX, CY, HOT)
        px(c, CX + 1, CY, HOT)
        px(c, CX, CY + 1, HOT)
    elif i == 1:                     # the shell splits into segments
        _shell(c, True)
        _cracks(c, True)
        for k in range(6):
            a = k * TAU / 6
            px(c, CX + math.cos(a) * 14, CY + math.sin(a) * 11, HOT)
    else:                            # chunks fly out and crumble
        t = i - 2
        for k in range(6):
            a = k * TAU / 6 + 0.15
            d = 6 + t * 9
            x = CX + math.cos(a) * d
            y = CY + math.sin(a) * d * 0.70
            _chunk(c, x, y, fade=(t >= 2))
            for s in (1, 2):
                px(c, CX + math.cos(a) * (d - s * 3),
                   CY + math.sin(a) * (d - s * 3) * 0.70, LIT if s == 1 else OUT)
    return c


ANIM = [("break", [frame(i) for i in range(6)], 18, False, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
