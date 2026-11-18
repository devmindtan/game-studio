#!/usr/bin/env python3
"""Generator cho "wolf" (Sói Rừng): quái lao có báo trước của vùng Rừng Âm U (Bách Ải, đợt 6A).

Nâng cấp 2026-11-18 (design/art/monster-upgrade.md): vai gồ, đầu chúi thấp chồm tới, lông gai lởm chởm, hàm há
nanh trắng miệng đỏ, mắt đỏ phát sáng, sẹo, móng trắng, đuôi xù gai. Khi gồng (attack frame 1) nó hạ thấp người; game vẽ dải đỏ
báo đường lao (Enemies.charge_lane). Frame 40x28, quay phải, neo giữa hai chân trên đất (20, 27), ground=True.
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
W, H = 40, 28
ANCHOR = (20.0, 27.0)
OUTLINE = "#0c0a10"
# Upgrade 2026-11-18 (games/bach-ai/design/art/monster-upgrade.md): hunched shoulders, head low and forward,
# jagged hackles, snarling red mouth with white fangs, glowing red eye, scar, white claws, spiky tail.
PAL = {"K": "#2a2836", "g": "#57536a", "l": "#8a86a0", "s": "#b4b0c8", "b": "#a29cb2", "r": "#b01c2c",
       "R": "#5a0c14", "t": "#f4ecdc", "e": "#ff3a2a", "E": "#ffd8a0", "n": "#0c0a10", "c": "#c06060"}
BODY = [
    "..................s..s..................",
    "...............sKsKsKKs.................",
    ".............sKgllgllgKs.......KK.......",
    "...........sKgllllllllggK.....KlgK......",
    "ss.......sKgllllgggggggggKK..KllggK.....",
    "sKs....KKglllggggggggggggggKKglgggKK....",
    ".sKgsKKggllgggggggggggggggggggggggeEKK..",
    "..sKggglgggggggggggggggggggggggggggggKKn",
    "...sKgggggcggggggggggggggggggggggKtRrrrK",
    "....KKggggcgggggggggggggggggggggKtRRRRK.",
    "......KgggggggggggggggggbbbbbbbKKtRtRtK.",
    ".......KgggbbbbbbbbbbbbbbbbbbbbbKKKKKK..",
    "........KKgbbbbbbbbbbbbbbbgggKKKK.......",
]
LEGS = {
    0: [".........KgK.KgK...........KgK.KgK.....", "........KgK...KgK.........KgK...KgK....",
        ".......KgK.....KgK.......KgK.....KgK...", "......KgK.......KgK.....KgK.......KgK..",
        ".....KtK.........KtK...KtK.........KtK."],
    1: [".........KgKKgK.............KgKKgK.....", ".........KgKKgK.............KgKKgK.....",
        ".........KgKKgK.............KgKKgK.....", ".........KgKKgK.............KgKKgK.....",
        "........KtKKKtK............KtKKKtK....."],
    2: [".........KgK.KgK...........KgK.KgK.....", "..........KgKKgK............KgKKgK.....",
        "...........KgKgK.............KgKgK.....", "............KgKgK.............KgKgK....",
        "............KtKtK.............KtKtK...."],
    3: [".........KgKKgK.............KgKKgK.....", ".........KgKKgK.............KgKKgK.....",
        ".........KgKKgK.............KgKKgK.....", ".........KgKKgK.............KgKKgK.....",
        "........KtKKKtK............KtKKKtK....."],
}


def wolf(legs=0, dy=0, dx=0, crouch=False, glare=False):
    rows = list(BODY)
    if glare:   # the eye flares before the dash
        rows[6] = rows[6].replace("eE", "EE")
    lg = LEGS[legs] if not crouch else LEGS[1][2:]
    art = from_rows([r.ljust(40, ".") for r in rows + lg], PAL)
    c = Canvas(W, H)
    c.paste(art, (W - art.width) // 2 + dx, 25 - (art.height - 1) + dy)
    if glare:
        for x, y in ((art.width - 2 + dx, 5 + 26 - (art.height - 1) + dy), (art.width + dx, 6 + 26 - (art.height - 1) + dy)):
            if 0 <= x < W and 0 <= y < H:
                c.pixel(x, y, "#ff8a5a")
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, gg, b, a = px[xx, yy]
            if a and (r, gg, b) != (0x0c, 0x0a, 0x10):
                px[xx, yy] = (round(r + (255 - r) * amount), round(gg + (255 - gg) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def fallen(fade=0.0):
    rows = [
        "...................................KK...",
        "..........sKsKsKs................KglK...",
        "ss....KKKgllllllllgKKKKKKKKKKKKKKglgKK..",
        ".sKgKKggggggggggggggggggggggggggggggKRK.",
        "..KKggggcggggggggggggggggggbbbbbbbKtRtK.",
        "....KgbbbbbbbbbbbbbbbbbbbbbbbbgKKKKKK...",
        "....KtKgKtK.........KtKgKtK.............",
    ]
    art = from_rows([r.ljust(40, ".") for r in rows], PAL)
    c = Canvas(W, H)
    c.paste(art, 0, 25 - (art.height - 1))
    c = c.outline(OUTLINE)
    if fade:
        px = c.img.load()
        for yy in range(c.height):
            for xx in range(c.width):
                if px[xx, yy][3] and (xx + yy) % 4 < round(fade * 4):
                    px[xx, yy] = (0, 0, 0, 0)
    return c


HB = {"shape": "rect", "center": [20.0, 27.0]}
ANIMATIONS = [
    ("move", [wolf(0), wolf(1), wolf(2), wolf(3)], 12, True,
     {"durations_ms": [90, 90, 90, 90], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [wolf(1, 0, -1, crouch=True, glare=True), wolf(0, 0, 3, glare=True), wolf(2, 0, 1)], 12, False,
     {"durations_ms": [220, 120, 140], "hitbox": {**HB, "active": [1, 2]}}),
    ("hurt", [flash(wolf(1)), wolf(1, 0, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(wolf(1), 0.5), fallen(), fallen(0.25), fallen(0.6)], 10, False,
     {"durations_ms": [90, 160, 160, 240], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
