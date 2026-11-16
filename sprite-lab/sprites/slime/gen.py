#!/usr/bin/env python3
"""Generator cho sprite "slime": quái vùng 1 (Bách Ải), khối thạch xanh ngọc, mắt to, nảy khi bò.

Frame 24x24, nhìn ngang quay phải, neo (12, 23) = giữa đáy trên mặt đất (ground=True).
Hình là bản đồ pixel vẽ tay cho 4 dáng (thường, bẹt, vươn, xẹp); animation chỉ chọn dáng + mắt.
Animation: move 4 (nảy: thường → bẹt → vươn → thường), attack 3 (lấy đà bẹt, chồm tới), hurt 2 (nháy trắng),
death 4 (xẹp thành vũng rồi tan).  Chạy: gamekit art run slime
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

from spritekit import Canvas, from_rows  # noqa: E402
from sheet import export  # noqa: E402

NAME = "slime"
SIZE = 24
ANCHOR = (12.0, 23.0)   # outline under the body is row 22
OUTLINE = "#1b1726"
PAL = {
    "m": "#4cc9a0",   # body
    "d": "#2f8a6e",   # shade (bottom, back)
    "l": "#a6f0d0",   # light (top front)
    "w": "#ffffff",   # gloss
    "e": "#1b1726",   # eye
    "p": "#ffffff",   # pupil glint
    "t": "#2a6b56",   # puddle
}

# Hand-drawn shapes, facing right; the last row is the bottom of the body (row 21 in the frame).
SHAPES = {
    "normal": [
        "......mmmmmm......",
        "....mmmmmmmmmm....",
        "...mmmmlllmmmmm...",
        "..mmmmlwwlmmmmmm..",
        "..mmmmmllmmeemmm..",
        ".mmmmmmmmmmeepmmm.",
        ".mmmmmmmmmmeemmmm.",
        ".dmmmmmmmmmmmmmmm.",
        ".ddmmmmmmmmmmmmmd.",
        "..dddmmmmmmmmmdd..",
        "...ddddddddddddd..",
    ],
    "squash": [
        "......mmmmmmm.......",
        "...mmmmmllmmmmmm....",
        "..mmmmlwwlmmmmmmm...",
        ".mmmmmmllmmmmeemmm..",
        "mmmmmmmmmmmmmeepmmm.",
        "dmmmmmmmmmmmmmmmmmm.",
        "ddmmmmmmmmmmmmmmmmd.",
        ".ddddmmmmmmmmmmmddd.",
        "..dddddddddddddddd..",
    ],
    "stretch": [
        "......mmmm......",
        ".....mmmmmm.....",
        "....mmlllmmm....",
        "...mmlwwlmmmm...",
        "...mmmllmmeem...",
        "..mmmmmmmmeepm..",
        "..mmmmmmmmeemm..",
        "..mmmmmmmmmmmm..",
        "..dmmmmmmmmmmm..",
        "..ddmmmmmmmmmd..",
        "...ddmmmmmmdd...",
        "....dddddddd....",
    ],
    "flat": [
        "........mmmmm.........",
        ".....mmmmmmmmmmmm.....",
        "..ddmmmmmmmmmmmmmmdd..",
        "tdddddddddddddddddddt.",
    ],
    "puddle": [
        "....tttttttttttttt....",
        "..tttttttttttttttttt..",
    ],
}


def shape(name: str, dx: int = 0, eyes: str = "open") -> Canvas:
    rows = SHAPES[name]
    if eyes == "closed":
        rows = [r.replace("p", "e") for r in rows]
        rows = [r.replace("ee", "..") if i in (4, 3) else r for i, r in enumerate(rows)]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    x = (SIZE - art.width) // 2 + dx
    y = 21 - (art.height - 1)            # bottom row of the art on row 21
    c.paste(art, x, y)
    return c.outline(OUTLINE)


def flash(c: Canvas, amount: float = 0.75) -> Canvas:
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x1b, 0x17, 0x26):          # keep the outline dark
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


ANIMATIONS = [
    ("move", [shape("normal"), shape("squash"), shape("stretch"), shape("normal")], 8, True,
     {"durations_ms": [120, 100, 140, 120]}),
    ("attack", [shape("squash", -1), shape("squash", -2), shape("stretch", 2)], 10, False,
     {"durations_ms": [160, 120, 140]}),
    ("hurt", [flash(shape("squash", eyes="closed")), shape("normal", eyes="closed")], 12, False,
     {"durations_ms": [80, 120]}),
    ("death", [shape("squash", eyes="closed"), shape("flat"), shape("puddle"),
               shape("puddle").copy()], 8, False, {"durations_ms": [90, 110, 200, 300]}),
]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move")
    print(f"strip: {HERE / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
