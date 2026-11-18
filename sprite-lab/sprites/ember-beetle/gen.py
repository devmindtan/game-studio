#!/usr/bin/env python3
"""Generator cho "ember-beetle" (Bọ Lửa): quái nổ khi chết của vùng Đồng cỏ (Bách Ải, đợt 6A).

Con bọ cánh cứng đen bóng, bụng là túi than đỏ cam phát sáng (dấu hiệu "sẽ nổ"), sáu chân ngắn chạy nhanh.
Khi chết bụng sáng trắng rồi vỡ: game đặt vòng cảnh báo và nổ sau đó (design 6A).
Frame 24x24, quay phải, neo (12, 23) (ground=True). move 4 (chân so le, bụng nhấp nháy), attack 3 (nhún, lao),
hurt 2, death 4 (bụng phồng sáng → vỡ → khói).  Chạy: gamekit art run ember-beetle
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

NAME = "ember-beetle"
SIZE = 24
ANCHOR = (12.0, 23.0)
OUTLINE = "#1b1726"
PAL = {
    "k": "#2a2238", "K": "#453a5c", "h": "#7a6c9a",   # shell: dark, mid, gloss
    "o": "#f06a2a", "y": "#ffc04a", "w": "#fff2b0",   # ember belly: orange, yellow, white-hot
    "r": "#a8301e",                                    # belly shade
    "e": "#ffd04a",                                    # eye
    "l": "#3a2a2a",                                    # legs
    "s": "#6a6070", "S": "#9a90a0",                    # smoke
}

BODY = {
    "dim": [
        "......KKKKK.......",
        "....KKhhKKKKk.....",
        "...KhhKKKKKKKkk...",
        "..rooyyoKKKKKKkKe.",
        ".rooyyyyoKKKKKKKK.",
        ".rroooooKKKKKKKk..",
        "..rrrrrkkkkkkkk...",
    ],
    "glow": [
        "......KKKKK.......",
        "....KKhhKKKKk.....",
        "...KhhKKKKKKKkk...",
        "..ryywwyyKKKKKkKe.",
        ".ryywwwwyKKKKKKKK.",
        ".rryyyyyKKKKKKKk..",
        "..rrrrrkkkkkkkk...",
    ],
}
LEGS = {0: [".l.l..l..l.l.l....", "l...l...l...l....."], 1: ["..l.l..l..l.l.....", ".l...l...l...l...."]}


def beetle(body="dim", legs=0, dx=0, squash=False):
    rows = list(BODY[body])
    if squash:
        rows = rows[1:]
    rows = rows + LEGS[legs]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2 + dx, 21 - (art.height - 1))
    return c.outline(OUTLINE)


def flash(c, amount=0.75):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x1b, 0x17, 0x26):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def burst(n):
    rows = {0: ["...y.w..y.....", ".y.wwwwww.y...", "yowwwwwwwwoy..", ".oyyyyyyyyo...", "..rrrrrrrr...."],
            1: ["s..y...o..s...", "..o.y.w.y.....", "o..y.w.y..o...", ".s..o..o..s...", "...ssssss....."],
            2: ["..S...s...S...", "...sSs.sSs....", ".s..S...S..s..", "....sssss....."]}[n]
    art = from_rows([r.center(18, ".") for r in rows], PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, 21 - (art.height - 1))
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [12.0, 23.0]}
ANIMATIONS = [
    ("move", [beetle("dim", 0), beetle("dim", 1), beetle("glow", 0), beetle("dim", 1)], 12, True,
     {"durations_ms": [80, 80, 80, 80], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [beetle("glow", 0, -1, squash=True), beetle("glow", 1, 1), beetle("glow", 0, 2)], 12, False,
     {"durations_ms": [140, 90, 120], "hitbox": {**HB, "active": [0, 2]}}),
    ("hurt", [flash(beetle("glow", 0)), beetle("dim", 0)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(beetle("glow", 1), 0.5), burst(0), burst(1), burst(2)], 10, False,
     {"durations_ms": [100, 90, 140, 220], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
