#!/usr/bin/env python3
"""Generator cho "wolf" (Sói Rừng): quái lao có báo trước của vùng Rừng Âm U (Bách Ải, đợt 6A).

Sói xám đen gầy, lưng gù, mắt vàng, đuôi rủ. Khi gồng (attack frame 1) nó hạ thấp người; game vẽ dải đỏ
báo đường lao (Enemies.charge_lane). Frame 32x24, quay phải, neo giữa hai chân trên đất (16, 23), ground=True.
move 4 (phi nước kiệu), attack 3 (hạ người → vồ → hạ cánh), hurt 2, death 4 (ngã, mờ dần).
Chạy: gamekit art run wolf
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

NAME = "wolf"
W, H = 32, 24
ANCHOR = (16.0, 23.0)
OUTLINE = "#14121c"
PAL = {
    "k": "#3a3848",   # dark fur (outline side, far legs)
    "g": "#646076",   # fur
    "l": "#9490a8",   # lit back
    "b": "#b8b2c4",   # belly / muzzle / chest
    "e": "#ffd040",   # eye
    "t": "#f0e8d8",   # fangs
    "n": "#14121c",   # nose
}

# 24 wide: bushy tail left, raised hackles, long pointed snout right
BODY = [
    "................k.k.....",
    "...............kgkgk....",
    "..............kggggk....",
    "l.......lllllkgggggggg..",
    "ll....llgggglggggegggbbn",
    ".lllllgggggggggggggbbbt.",
    "..kgggggggggggggggggb...",
    "...kggggggggggggggk.....",
    "....kbbbbbbbbbbbgk......",
]
LEGS = {
    0: ["....kg........gk.......", "...k..g......g..k......", "..k....g....g....k.....", ".kk....gg..gg.....kk..."],
    1: ["....kg........gk.......", "....kg........gk.......", "....kg........gk.......", "....kgg.......gkk......"],
    2: ["....gk........kg.......", ".....g.k.....k.g.......", "......g.k...k..g.......", "......gg.kkk...gg......"],
    3: ["....kg........gk.......", "....kg........gk.......", "....kg........gk.......", "....kgg.......gkk......"],
}


def wolf(legs=0, dy=0, dx=0, crouch=False):
    rows = list(BODY)
    if crouch:
        rows = rows[1:]
    lg = LEGS[legs] if not crouch else LEGS[1][2:]
    art = from_rows(rows + lg, PAL)
    c = Canvas(W, H)
    c.paste(art, (W - art.width) // 2 + dx, 21 - (art.height - 1) + dy)
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x14, 0x12, 0x1c):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def fallen(fade=0.0):
    rows = [
        "........................",
        ".......llllll......kk...",
        "ll..kllgggggglllllkggk..",
        ".llgggggggggggggggggggbn",
        "..kgbbbbbbbbbbbbgggkgb..",
        "...kgg.kgg....kgg.kgg...",
    ]
    art = from_rows(rows, PAL)
    c = Canvas(W, H)
    c.paste(art, (W - art.width) // 2, 21 - (art.height - 1))
    c = c.outline(OUTLINE)
    if fade:
        px = c.img.load()
        for yy in range(c.height):
            for xx in range(c.width):
                r, g, b, a = px[xx, yy]
                if a and (xx + yy) % 4 < round(fade * 4):
                    px[xx, yy] = (0, 0, 0, 0)
    return c


HB = {"shape": "rect", "center": [16.0, 23.0]}
ANIMATIONS = [
    ("move", [wolf(0), wolf(1), wolf(2), wolf(3)], 12, True,
     {"durations_ms": [90, 90, 90, 90], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [wolf(1, 0, -1, crouch=True), wolf(2, 0, 3), wolf(0, 0, 1)], 12, False,
     {"durations_ms": [200, 120, 140], "hitbox": {**HB, "active": [1, 2]}}),
    ("hurt", [flash(wolf(1)), wolf(1, 0, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(wolf(1), 0.5), fallen(), fallen(0.25), fallen(0.6)], 10, False,
     {"durations_ms": [90, 160, 160, 240], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
