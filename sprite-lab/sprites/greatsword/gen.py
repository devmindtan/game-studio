#!/usr/bin/env python3
"""Generator cho sprite "greatsword": đại kiếm (vật phẩm/trang bị, legacy).

  idle    1 frame: đại kiếm lớn, lưỡi thẳng, cân đối.

Neo (14, 30) gần chuôi (sprite 32x32).

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
ANCHOR = (14.0, 30.0)

BLADE = "#b8c7d9"; BLADE_D = "#6b7f96"; BLADE_L = "#d8e4f0"; EDGE = "#f2fbff"
HILT = "#8a5a2e"; HILT_D = "#563418"; GUARD = "#d9b44a"; POMMEL = "#d9b44a"


def blade_draw(c, glint=False):
    # lưỡi thẳng, rộng, chéo lên-phải
    for j, y in enumerate(range(5, 25)):
        x = 22 - j
        c.pixel(x, y, BLADE_L)
    for j, y in enumerate(range(5, 26)):
        x = 21 - j
        c.pixel(x, y, BLADE)
        c.pixel(x - 1, y, BLADE)
    for j, y in enumerate(range(6, 26)):
        x = 19 - j
        c.pixel(x, y, BLADE_D)
    for j, y in enumerate(range(8, 23)):
        x = 20 - j
        c.pixel(x, y, BLADE_D)
    # tip
    c.pixel(22, 4, EDGE); c.pixel(21, 4, BLADE_L); c.pixel(22, 5, BLADE_L); c.pixel(21, 5, BLADE)
    # guard
    c.line(5, 24, 14, 21, GUARD); c.line(5, 25, 14, 22, HILT_D)
    c.pixel(5, 24, GUARD); c.pixel(14, 21, GUARD)
    # grip
    c.line(10, 23, 8, 30, HILT)
    c.pixel(10, 24, HILT_D); c.pixel(9, 26, HILT_D); c.pixel(8, 28, HILT_D)
    c.rect(7, 29, 9, 30, POMMEL)
    if glint:
        c.pixel(20, 8, EDGE); c.pixel(18, 12, EDGE); c.pixel(16, 16, EDGE)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(7, 29, 16, 31, "#00000033")
    blade_draw(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(0)], 1, False,
               {"hitbox": {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": [0, 0]}})]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")


if __name__ == "__main__":
    main()
