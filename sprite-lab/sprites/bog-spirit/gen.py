#!/usr/bin/env python3
"""Generator cho "bog-spirit" (Hồn Đầm): quái hỗ trợ của vùng Đầm Lầy Độc (Bách Ải, đợt 6A).

Một bóng ma đầm lầy còng lưng, áo choàng rêu rách tả tơi, mặt tối với hai mắt trắng, tay cầm đèn lồng
xanh lục phát sáng. Nó lơ lửng (đuôi áo tan dần), giữ khoảng cách và giơ đèn hồi máu cho quái quanh nó.
Vật bay: frame 24x24, neo ở tâm thân (12, 12), ground=False.
move 4 (lơ lửng nhấp nhô, đèn đung đưa), attack 3 (giơ đèn, đèn bùng sáng), hurt 2, death 4 (tan thành rêu và đốm sáng).
Chạy: gamekit art run bog-spirit
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas, from_rows  # noqa: E402
from sheet import export  # noqa: E402

NAME = "bog-spirit"
SIZE = 24
ANCHOR = (12.0, 12.0)
OUTLINE = "#0e140e"
PAL = {
    "d": "#2a3a22",   # cloak shade
    "m": "#46603a",   # moss cloak
    "l": "#6e8a4a",   # lit moss
    "f": "#121812",   # face hollow
    "w": "#e8f0e0",   # eyes
    "s": "#5a4a30",   # lantern pole
    "g": "#7aff8a",   # lantern glow
    "G": "#d8ffd8",   # lantern core
}

BODY = [
    "....lllll.....",
    "...lmmmmml....",
    "..lmffffmml...",
    "..mfwffwfmm...",
    "..mffffffmd...",
    ".lmmffffmmmd..",
    ".mmmmmmmmmmd..",
    "lmmdmmmmdmmdd.",
    "mmdmmmmmmdmmd.",
]
TAILS = [
    [".mdmm.mmdmd...", "..d.m..m.d....", "....d...d....."],
    ["..mdmmmdmm....", "..m..d.m.d....", "...d....d....."],
    [".mdmmmdmmd....", "...m.d..m.d...", "....d.....d..."],
    ["..mmdmmdmm....", ".d..m..d.m....", "..d....d......"],
]


def lantern(c, x, y, bright=False):
    c.line(x, y - 6, x, y, PAL["s"])
    c.rect(x - 1, y + 1, x + 1, y + 3, PAL["G"] if bright else PAL["g"], fill=True)
    c.pixel(x, y + 2, PAL["G"])
    if bright:
        for dx, dy in ((-3, 2), (3, 2), (0, -1), (0, 6), (-2, 5), (2, 5)):
            c.pixel(x + dx, y + dy, PAL["g"])


def spirit(f=0, dy=0, sway=0, raise_lamp=False, bright=False):
    art = from_rows(BODY + TAILS[f % 4], PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, 3, 12 - 6 + dy)
    # a ragged sleeve reaching from the cloak to the lantern pole: the spirit holds it
    if raise_lamp:
        c.line(14, 11 + dy, 17, 5 + dy, PAL["m"], 2)
        c.pixel(17, 4 + dy, PAL["l"])
        lantern(c, 18, 2 + dy, bright)
    else:
        c.line(14, 12 + dy, 17 + sway, 9 + dy, PAL["m"], 2)
        c.pixel(17 + sway, 8 + dy, PAL["l"])
        lantern(c, 18 + sway, 10 + dy, bright)
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x0e, 0x14, 0x0e):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def fade(n):
    rows = {0: ["...l.g..l....", "..mmlmmlm.g..", ".l.mmGmm.l...", "..m.dmd.m....", "...d...d....."],
            1: ["..l....g.....", ".m..l.m..l...", "...g..m..g...", "..d...d......"],
            2: [".g.......g...", "....l..l.....", "..d.....d...."]}[n]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, 5, 12 - 2 - n)
    return c


HB = {"shape": "rect", "center": [12.0, 12.0]}
ANIMATIONS = [
    ("move", [spirit(0, 0, 0), spirit(1, -1, 1), spirit(2, -1, 0), spirit(3, 0, -1)], 8, True,
     {"durations_ms": [140, 140, 140, 140], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [spirit(0, 0, 0, True), spirit(1, -1, 0, True, True), spirit(2, 0, 0, True, True)], 8, False,
     {"durations_ms": [160, 200, 220], "hitbox": {**HB, "active": [0, 2]}}),
    ("hurt", [flash(spirit(0)), spirit(1, 0, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(spirit(2, 0, 0, False, True), 0.5), fade(0), fade(1), fade(2)], 8, False,
     {"durations_ms": [100, 140, 160, 240], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=False, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
