#!/usr/bin/env python3
"""Generator cho sprite "war-hammer": búa chiến (vật phẩm/trang bị).

  idle    1 frame: búa chiến, đầu vuông một bên và mỏ nhọn bên kia.

Neo (16, 30) đáy cán (sprite 32x32).

Chạy:  gamekit art run war-hammer
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

NAME = "war-hammer"
W, H = 32, 32
ANCHOR = (16.0, 30.0)

HEAD = "#b8c7d9"; HEAD_D = "#5f7187"; HEAD_L = "#d8e4f0"; EDGE = "#f2fbff"
HILT = "#8a5a2e"; HILT_D = "#563418"; BAND = "#d9b44a"; DARK = "#3a4657"


def hammer(c, glint=False):
    # cán thẳng
    c.rect(15, 11, 17, 30, HILT)
    c.line(15, 11, 15, 30, HILT_D)
    c.line(17, 11, 17, 30, HEAD_L)
    c.pixel(15, 30, HILT_D); c.pixel(16, 30, HILT); c.pixel(17, 30, HEAD_L)
    # đầu búa vuông (bên phải)
    c.rect(17, 4, 25, 11, HEAD_D)
    c.rect(18, 5, 24, 10, HEAD)
    c.rect(19, 5, 23, 6, HEAD_L)
    c.line(17, 4, 25, 4, EDGE); c.line(25, 4, 25, 11, HEAD_D); c.line(17, 11, 25, 11, HEAD_D)
    c.rect(24, 6, 25, 9, DARK)  # mặt đập
    # mỏ nhọn (bên trái)
    c.pixel(14, 7, HEAD_D); c.pixel(13, 7, HEAD_D); c.pixel(12, 7, HEAD_D); c.pixel(11, 7, HEAD)
    c.pixel(10, 8, HEAD); c.pixel(11, 8, HEAD_L)
    c.pixel(14, 8, HEAD); c.pixel(13, 8, HEAD); c.pixel(12, 8, HEAD_L)
    c.pixel(14, 9, HEAD_D); c.pixel(13, 9, HEAD_D); c.pixel(12, 9, HEAD); c.pixel(11, 9, HEAD)
    c.pixel(10, 8, EDGE)
    # vòng siết
    c.rect(14, 10, 18, 11, BAND)
    if glint:
        c.pixel(20, 5, EDGE); c.pixel(23, 5, EDGE)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(11, 29, 21, 31, "#00000033")
    hammer(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(0)], 1, False,
               {"hitbox": {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": [0, 0]}})]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print(f"ok")


if __name__ == "__main__":
    main()
