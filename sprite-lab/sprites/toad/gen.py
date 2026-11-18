#!/usr/bin/env python3
"""Generator cho "toad" (Cóc Độc): quái nhảy của vùng Đầm Lầy Độc (Bách Ải, đợt 6A).

Con cóc mập, lưng ô liu sẫm có mụn đốm cam độc, bụng vàng nhạt, mắt lồi vàng đồng tử đen, chân sau gập.
Nó ngồi thu mình, rồi bật tới chỗ người chơi; chỗ đáp để lại vũng độc (game vẽ, Enemies.add_pool).
Frame 24x24, quay phải, neo giữa chân trên đất (12, 23), ground=True.
move 4 (nhích người, họng phập phồng), attack 3 (thu mình → bật dài → đáp bẹp), hurt 2, death 4 (bẹp, vỡ thành vũng).
Chạy: gamekit art run toad
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

NAME = "toad"
SIZE = 24
ANCHOR = (12.0, 23.0)
OUTLINE = "#14160c"
PAL = {
    "d": "#2e3a1a",   # back shade
    "g": "#4a5a24",   # back olive
    "l": "#6e7e34",   # lit back
    "o": "#e8862a",   # poison spots
    "y": "#d8d07a",   # belly
    "Y": "#f0eaa0",   # throat (puffs)
    "e": "#f0c040",   # eye
    "p": "#14160c",   # pupil
}

SIT = [
    "......ee....ee....",
    ".....epe...epe....",
    "....gggglllgggg...",
    "...gglolggglolgg..",
    "..ggggggggoggggggd",
    ".dgggoggggggggggYd",
    ".dggggggggggggyYY.",
    "dddgggggggggyyyy..",
    "dd.dgg..dddd.dgg..",
]
PUFF = list(SIT)
PUFF[5] = ".dgggoggggggggggYY"
PUFF[6] = ".dggggggggggggyYYY"
CROUCH = SIT[:1] + SIT[2:4] + ["..ggggggggoggggggd", ".dggggggggggggyyYd", "dddddgggggggyyyyy.", "dd..ddd.dddd.ddd.."]
LEAP = [
    ".........ee..ee.......",
    "........epe.epe.......",
    "..d...ggggllllgggg....",
    ".dd..gglolggglolgggg..",
    "dd.dggggggggoggggggggd",
    "....dgggggggggggggyyYd",
    ".....ddgggggggggyyyY..",
]
FLAT = [
    "......ee.....ee.....",
    "...gggggllllllgggg..",
    ".ggglolgggoggglolggg",
    "dddddddddddddyyyyyyd",
]


def toad(rows, dx=0, dy=0):
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2 + dx, 21 - (art.height - 1) + dy)
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x14, 0x16, 0x0c):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def puddle(n):
    rows = {0: ["...l..o..l...", ".ggggggggggg.", "glgoggggoglgg", ".ddddddddddd."],
            1: [".....o.......", "..lggggggl...", ".ggggoggggg..", "..ddddddd...."],
            2: ["..g.....g....", "...ggggg.....", "....ddd......"]}[n]
    art = from_rows([r.center(16, ".") for r in rows], PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, 21 - (art.height - 1))
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [12.0, 23.0]}
ANIMATIONS = [
    ("move", [toad(SIT), toad(PUFF), toad(SIT, 1), toad(PUFF, 1)], 8, True,
     {"durations_ms": [160, 140, 160, 140], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [toad(CROUCH), toad(LEAP, 1), toad(FLAT)], 10, False,
     {"durations_ms": [220, 160, 200], "hitbox": {**HB, "active": [1, 2]}}),
    ("hurt", [flash(toad(SIT)), toad(SIT, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(toad(FLAT), 0.4), puddle(0), puddle(1), puddle(2)], 8, False,
     {"durations_ms": [100, 160, 180, 240], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
