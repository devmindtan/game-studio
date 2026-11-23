#!/usr/bin/env python3
"""Generator cho "bo-sim" (Bọ sim, Thất Tinh Ấn): bọ mai tím màu sim chín, bay vo ve thấp, cánh rung.
Người dùng chọn phương án C (sprite-lab/designs/dong-que-mobs/variants.py, 2026-11-23). Chuẩn creature-v1.
Frame 32x32, quay phải, vật bay: neo = tâm thân (16, 18). Bóng dưới đất do game vẽ, không nằm trong sprite.
Chạy: gamekit art run bo-sim
"""
import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("workspace?")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "bo-sim"
N = 32
ANCHOR = (16.0, 18.0)
OUT = "#1b1726"
SHELL, SHELL_D, SHELL_L, HEAD, EYE, WING, WING_D, LEG = "#6b3f8f", "#4a2a66", "#9a6ac0", "#2a2230", "#e0b250", "#c8d8f0", "#8aa0c0", "#2a2230"


def box(c, x0, y0, x1, y1, col):
    c.rect(int(x0), int(y0), int(x1), int(y1), col)


def px(c, x, y, col):
    c.pixel(int(round(x)), int(round(y)), col)


def bug(h=0, wing=0, tilt=0, eye="open", flash=0.0, flip=False, fade=1.0, legs=0, horn=0):
    """h: độ cao (-) lên; wing: 0 cánh xuôi, 1 cánh dựng, 2 cánh mở; tilt: chúi đầu (+); flip: lật ngửa (chết)."""
    c = Canvas(N, N)
    y = 15 + h
    # chân thõng (lắc theo nhịp)
    for k in range(3):
        px(c, 12 + k * 3, y + 6 + (k + legs) % 2, LEG)
    # mai
    for r in range(6):
        w = [3, 5, 6, 6, 5, 3][r]
        box(c, 16 - w, y + r, 15 + w, y + r, SHELL if r > 0 else SHELL_L)
    box(c, 16, y + 1, 16, y + 5, SHELL_D)
    for (dx, dy) in ((-3, 2), (2, 3), (4, 1)):
        px(c, 16 + dx, y + dy, SHELL_L)
    # đầu + mắt + râu
    hy = y + 1 + max(-2, min(2, tilt))
    box(c, 21, hy, 24, hy + 3, HEAD)
    px(c, 23, hy + 1, EYE if eye == "open" else "#e05050")
    if eye == "x":
        px(c, 22, hy + 1, "#e05050")
    px(c, 25, hy - 1 - horn, HEAD); px(c, 26, hy - 2 - horn, HEAD)
    # cánh (trong suốt nhẹ)
    if wing == 0:
        box(c, 9, y - 2, 16, y - 1, WING)
    elif wing == 1:
        box(c, 12, y - 6, 16, y - 1, WING); box(c, 12, y - 6, 12, y - 1, WING_D)
    else:
        box(c, 7, y - 4, 14, y - 1, WING); box(c, 14, y - 7, 18, y - 2, WING_D)
    c.outline(OUT)
    p = c.img.load()
    for yy in range(N):
        for xx in range(N):
            r, g, b, a = p[xx, yy]
            if not a:
                continue
            if flash and (r, g, b) != (0x1b, 0x17, 0x26):
                r, g, b = (round(r + (255 - r) * flash), round(g + (255 - g) * flash), round(b + (255 - b) * flash))
            p[xx, yy] = (r, g, b, round(a * fade))
    if flip:
        c.img = c.img.transpose(1)   # FLIP_TOP_BOTTOM: ngửa bụng
    return c


MOVE = [bug(h=[0, -1, -2, -2, -1, 0][i], wing=[0, 1, 2, 1, 0, 2][i], tilt=[0, 0, 1, 0, 0, -1][i], legs=i) for i in range(6)]
ATTACK = [  # gồng: bay vọt lên, chổng đuôi, sừng dựng, mắt đỏ → lao chúi xuống → bật về
    bug(h=-3, wing=2, tilt=-2, horn=1, eye="mad"),
    bug(h=-5, wing=1, tilt=-3, horn=1, eye="mad"),
    bug(h=1, wing=0, tilt=3, horn=1, eye="mad"),
    bug(h=3, wing=0, tilt=4, eye="mad"),
    bug(h=0, wing=2, tilt=1),
    bug(h=-1, wing=1, tilt=0),
]
HURT = [bug(h=-1, wing=2, tilt=-2, flash=0.75), bug(h=-2, wing=2, tilt=-3, eye="mad"), bug(h=0, wing=1)]
DEATH = [
    bug(h=-1, wing=2, tilt=-2, eye="x", flash=0.6),
    bug(h=1, wing=2, tilt=2, eye="x"),
    bug(h=4, wing=0, tilt=3, eye="x"),
    bug(h=6, wing=0, eye="x", flip=True),
    bug(h=6, wing=0, eye="x", flip=True, fade=0.55),
    bug(h=6, wing=0, eye="x", flip=True, fade=0.2),
]

ANIMATIONS = [
    ("move", MOVE, 12, True, {}),
    ("attack", ATTACK, 10, False, {"durations_ms": [140, 160, 60, 90, 110, 120],
                                   "hitbox": {"shape": "circle", "center": [18.0, 19.0], "active": [2, 3]}}),
    ("hurt", HURT, 12, False, {"durations_ms": [80, 110, 120]}),
    ("death", DEATH, 8, False, {"durations_ms": [90, 90, 90, 200, 150, 150]}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=False, body="move")
    print(f"OK {NAME}")
