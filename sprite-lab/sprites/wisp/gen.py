#!/usr/bin/env python3
"""Generator cho "wisp" (Ma Trơi): quái bay zig-zag của vùng Rừng Âm U (Bách Ải, đợt 6A).

Một đốm lửa ma xanh lục lam: lõi trắng nhạt, thân lửa xanh, ngọn lửa lay trên đỉnh, đuôi mảnh phía dưới,
hai mắt tối. Vật bay: frame 24x24, neo ở tâm thân (12, 12), ground=False.
move 4 (ngọn lửa lay, thân nhấp nhô), attack 3 (bùng sáng, lao), hurt 2, death 4 (tan thành đốm sáng).
Chạy: gamekit art run wisp
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

NAME = "wisp"
SIZE = 24
ANCHOR = (12.0, 12.0)
OUTLINE = "#0e1a22"
PAL = {
    "d": "#1f6a72",   # flame rim (deep teal)
    "m": "#3ac0b0",   # flame body
    "l": "#9af0d8",   # light
    "w": "#eafff6",   # white core
    "e": "#0e1a22",   # eyes
}

# body: rows centred on x=12; tips[f] = the flickering flame top (3 rows), tail[f] = wisp tail
BODY = [
    "...dmmmmd...",
    "..dmllllmd..",
    ".dmlwwwwlmd.",
    ".dmlwewewld.",
    ".dmlwwwwlmd.",
    "..dmllllmd..",
    "...dmmmmd...",
]
TIPS = [
    ["....d.......", "...dm..d....", "..dmmddm...."],
    [".......d....", "...d..md....", "...mddmmd..."],
    [".....d......", "....dmd.....", "...dmlmd...."],
    ["...d....d...", "...md..dm...", "..dmmddmmd.."],
]
TAILS = [
    ["....dmmd....", ".....dd.....", "......d....."],
    ["....dmmd....", "....dd......", "...d........"],
    ["....dmmd....", ".....dd.....", ".....d......"],
    ["....dmmd....", "......dd....", "........d..."],
]


def wisp(f=0, dy=0, dx=0, bright=False):
    rows = TIPS[f % 4] + BODY + TAILS[f % 4]
    if bright:
        rows = [r.replace("m", "l").replace("d", "m") for r in rows]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    # body centre row (3 tip rows + 3) sits on the anchor
    c.paste(art, (SIZE - art.width) // 2 + dx, 12 - 6 + dy)
    return c.outline(OUTLINE)


def flash(c, amount=0.75):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x0e, 0x1a, 0x22):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def motes(n):
    """Dissolving: the flame breaks into drifting sparks."""
    rows = {0: ["...l..m..l..", ".m..wllw..m.", "..lwwwwwwl..", ".m..wllw..m.", "...l..m..l.."],
            1: ["l....m....l.", "..m..l..m...", ".l..w..w..l.", "..m..l..m...", "m....l....m."],
            2: ["d.........d.", "....m..m....", "..d......d..", "....m..m....", ".d........d."]}[n]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, 12 - 2 - n)
    return c


HB = {"shape": "rect", "center": [12.0, 12.0]}
ANIMATIONS = [
    ("move", [wisp(0, 0), wisp(1, -1), wisp(2, -1), wisp(3, 0)], 10, True,
     {"durations_ms": [110, 110, 110, 110], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [wisp(2, 0, 0, True), flash(wisp(0, -1, 1, True), 0.4), wisp(1, 0, 2, True)], 12, False,
     {"durations_ms": [140, 80, 120], "hitbox": {**HB, "active": [0, 2]}}),
    ("hurt", [flash(wisp(0)), wisp(1, 0, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(wisp(2, 0, 0, True), 0.6), motes(0), motes(1), motes(2)], 10, False,
     {"durations_ms": [90, 100, 140, 220], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=False, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
