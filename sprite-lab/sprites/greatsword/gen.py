#!/usr/bin/env python3
"""Generator cho sprite "greatsword": đại kiếm (vật phẩm/trang bị, legacy).

  idle    1 frame: đại kiếm lớn, lưỡi thẳng, cân đối.

Neo (11, 30) gần chuôi (sprite 32x32).

Chạy:  gamekit art run greatsword
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "greatsword"
W, H = 32, 32
ANCHOR = (11.0, 30.0)

BLADE = "#b8c7d9"; BLADE_D = "#6b7f96"; BLADE_L = "#d8e4f0"; EDGE = "#f2fbff"
HILT = "#8a5a2e"; HILT_D = "#563418"; GUARD = "#d9b44a"; POMMEL = "#d9b44a"


def blade_draw(c, glint=False):
    for i in range(19):
        x = 10 + i
        y = 25 - i
        c.pixel(x, y, BLADE_D)
        c.pixel(x, y - 1, BLADE)
        c.pixel(x, y - 2, BLADE)
        c.pixel(x - 1, y - 2, BLADE_L)
    for i in range(4, 15):
        x = 10 + i
        y = 25 - i
        c.pixel(x, y - 1, BLADE_D)
    c.pixel(28, 6, BLADE_L); c.pixel(29, 5, EDGE); c.pixel(28, 5, BLADE_L); c.pixel(29, 6, BLADE)
    c.line(7, 25, 13, 25, GUARD)
    c.line(7, 26, 13, 26, HILT_D)
    c.pixel(13, 24, GUARD)
    c.line(10, 27, 10, 29, HILT)
    c.line(9, 27, 9, 29, HILT_D)
    c.rect(9, 30, 11, 30, POMMEL)
    if glint:
        c.pixel(16, 18, EDGE); c.pixel(19, 15, EDGE); c.pixel(22, 12, EDGE)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(8, 29, 14, 31, "#00000033")
    blade_draw(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(0)], 1, False,
               {"hitbox": {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": [0, 0]}})]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")


if __name__ == "__main__":
    main()
