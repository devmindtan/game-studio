#!/usr/bin/env python3
"""Generator cho sprite "magic-staff": trượng phép gỗ (vật phẩm/trang bị, legacy).

  idle    1 frame: trượng gỗ thẳng, ngọc phép trên đầu.

Neo (12, 30) đáy trượng (sprite 24x32).

Chạy:  gamekit art run magic-staff
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

NAME = "magic-staff"
W, H = 24, 32
ANCHOR = (12.0, 30.0)

MAIN = "#b07c44"; DARK = "#7a4f2a"; LIGHT = "#d4a86a"; EDGE = "#e8cfa0"
TRIM = "#d9b44a"; TRIM_D = "#8f6a1f"
ORB = "#45a8ff"; ORB_L = "#9fd7ff"; ORB_D = "#2a5fb8"; CORE = "#ffffff"


def staff(c, glint=False):
    # thân gậy thẳng
    c.rect(11, 9, 13, 30, MAIN)
    c.line(11, 9, 11, 30, DARK)
    c.line(13, 9, 13, 30, LIGHT)
    c.pixel(11, 30, DARK); c.pixel(12, 30, MAIN); c.pixel(13, 30, LIGHT)
    # vòng trang trí
    c.line(10, 20, 14, 20, TRIM); c.pixel(10, 20, TRIM_D); c.pixel(14, 20, TRIM_D)
    c.line(10, 26, 14, 26, TRIM)
    # giá giữ ngọc
    c.line(11, 9, 10, 7, TRIM); c.line(13, 9, 14, 7, TRIM)
    c.line(10, 7, 11, 6, TRIM_D); c.line(14, 7, 13, 6, TRIM_D)
    c.rect(10, 8, 14, 9, TRIM)
    # ngọc phép
    c.ellipse(10, 2, 14, 6, ORB_D)
    c.ellipse(11, 3, 13, 5, ORB)
    c.pixel(11, 3, ORB_L); c.pixel(12, 4, CORE)
    if glint:
        c.pixel(13, 3, EDGE); c.pixel(9, 4, ORB_L); c.pixel(13, 14, EDGE)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 29, 15, 31, "#00000033")
    staff(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(0)], 1, False,
               {"hitbox": {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": [0, 0]}})]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")


if __name__ == "__main__":
    main()
