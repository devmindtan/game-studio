#!/usr/bin/env python3
"""Generator cho sprite "iron-sword": kiếm sắt (vật phẩm/trang bị, legacy).

  idle    1 frame: kiếm sắt, lưỡi thẳng, cân đối.

Neo (12, 22) gần chuôi (sprite 24x24).

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
ANCHOR = (12.0, 22.0)

BLADE = "#b8c7d9"; BLADE_D = "#6b7f96"; BLADE_L = "#d8e4f0"; EDGE = "#f2fbff"
HILT = "#8a5a2e"; HILT_D = "#563418"; GUARD = "#d9b44a"; POMMEL = "#d9b44a"


def sword(c, glint=False):
    # lưỡi kiếm thẳng, chéo lên-phải
    for x, y in [(16,5),(15,7),(14,9),(13,11),(12,13),(11,15),(10,17),(9,19)]:
        c.pixel(x, y, BLADE_L)
    for x, y in [(15,6),(14,8),(13,10),(12,12),(11,14),(10,16),(9,18),(8,20)]:
        c.pixel(x, y, BLADE)
    for x, y in [(14,7),(13,9),(12,11),(11,13),(10,15),(9,17),(8,19)]:
        c.pixel(x, y, BLADE_D)
    # tip
    c.pixel(17, 4, EDGE); c.pixel(16, 4, BLADE_L); c.pixel(17, 5, BLADE)
    c.pixel(13, 12, BLADE_D); c.pixel(12, 14, BLADE_D)
    # guard
    c.line(7, 19, 11, 17, GUARD); c.pixel(7, 19, GUARD); c.pixel(11, 17, GUARD)
    c.pixel(7, 20, HILT_D)
    # grip
    c.line(8, 20, 7, 22, HILT); c.pixel(8, 21, HILT_D)
    c.pixel(7, 22, POMMEL)
    if glint:
        c.pixel(15, 8, EDGE); c.pixel(14, 10, EDGE)


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
