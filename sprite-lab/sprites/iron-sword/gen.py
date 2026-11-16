#!/usr/bin/env python3
"""Generator cho sprite "iron-sword": kiếm sắt (vật phẩm/trang bị, legacy).

  idle    1 frame: kiếm sắt, lưỡi thẳng, cân đối.

Neo (10, 22) gần chuôi (sprite 24x24).

Chạy:  gamekit art run iron-sword
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

NAME = "iron-sword"
W, H = 24, 24
ANCHOR = (10.0, 22.0)

BLADE = "#b8c7d9"; BLADE_D = "#6b7f96"; BLADE_L = "#d8e4f0"; EDGE = "#f2fbff"
HILT = "#8a5a2e"; HILT_D = "#563418"; GUARD = "#d9b44a"; POMMEL = "#d9b44a"


def sword(c, glint=False):
    for i in range(13):
        x = 10 + i
        y = 18 - i
        c.pixel(x, y, BLADE_D)
        c.pixel(x, y - 1, BLADE)
        c.pixel(x - 1, y - 1, BLADE_L)
    c.pixel(22, 5, BLADE_L); c.pixel(23, 4, EDGE); c.pixel(22, 4, BLADE_L); c.pixel(23, 5, BLADE)
    c.line(8, 18, 12, 18, GUARD)
    c.pixel(8, 19, HILT_D); c.pixel(12, 17, GUARD)
    c.line(10, 19, 10, 21, HILT)
    c.line(9, 19, 9, 21, HILT_D)
    c.pixel(9, 22, POMMEL); c.pixel(10, 22, POMMEL)
    if glint:
        c.pixel(14, 13, EDGE); c.pixel(17, 10, EDGE)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(7, 21, 14, 23, "#00000033")
    sword(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(0)], 1, False,
               {"hitbox": {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": [0, 0]}})]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")


if __name__ == "__main__":
    main()
