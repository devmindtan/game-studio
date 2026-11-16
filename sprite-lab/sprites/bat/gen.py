#!/usr/bin/env python3
"""Generator cho sprite "bat": quái vùng 1 (Bách Ải), dơi tím than bay theo bầy, mắt đỏ, nhìn ngang quay phải.

Frame 24x24, quái bay: neo (12, 12) ở tâm thân (không ground). Thân + tai vẽ tay; 4 dáng cánh vẽ tay
(lên, ngang, xuống, ngang). Animation: move 4 (vỗ cánh), attack 3 (khép cánh, lao), hurt 2 (nháy trắng),
death 4 (cánh gập, rơi xuống).  Chạy: gamekit art run bat
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

NAME = "bat"
SIZE = 24
ANCHOR = (12.0, 12.0)
OUTLINE = "#1b1726"
PAL = {
    "b": "#4a3a6b",   # body
    "d": "#2f2448",   # shade
    "l": "#6e5a96",   # light
    "w": "#5b4a80",   # wing membrane
    "k": "#3a2d55",   # wing bone / dark edge
    "r": "#ff4f6d",   # eye
    "f": "#e8e8f0",   # fang
}

# 24-wide rows, body centred at column 12, facing right (ear + eye + fang on the right).
BODY = [
    "..........l..l..........",
    "..........bb.bb.........",
    ".........bbbbbbb........",
    ".........bblbbrb........",
    ".........bbbbbbb........",
    "..........bbbbf.........",
    "..........dbbbd.........",
    "...........ddd..........",
]
WINGS = {
    "up": [
        "..kk................kk..",
        "..kwk..............kwk..",
        "...kwwk..........kwwk...",
        "....kwwwk......kwwwk....",
        ".....kwwwk....kwwwk.....",
        "......kwwk....kwwk......",
    ],
    "mid": [
        "........................",
        "........................",
        "kk....................kk",
        "kwwkk..............kkwwk",
        ".kwwwwkk........kkwwwwk.",
        "..kkwwwk........kwwwkk..",
    ],
    "down": [
        "........................",
        "........................",
        "........................",
        "......kkk......kkk......",
        "....kkwwwk....kwwwkk....",
        "..kkwwwwk......kwwwwkk..",
        ".kwwwkk..........kkwwwk.",
        ".kk..................kk.",
    ],
    "folded": [
        "........................",
        "........................",
        "........................",
        ".......kk......kk.......",
        "........kwk..kwk........",
        ".........kk..kk.........",
    ],
}


def frame(wings: str, dy: int = 0, dx: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    w = from_rows(WINGS[wings], PAL)
    b = from_rows(BODY, PAL)
    top = 8 + dy                      # body occupies rows 8..15, centre ~12
    c.paste(w, dx, top + 1)
    c.paste(b, dx, top)
    return c.outline(OUTLINE)


def flash(c: Canvas, amount: float = 0.75) -> Canvas:
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x1b, 0x17, 0x26):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


ANIMATIONS = [
    ("move", [frame("up", -1), frame("mid"), frame("down", 1), frame("mid")], 12, True, {}),
    ("attack", [frame("up", -2), frame("folded", -1, -1), frame("folded", 0, 2)], 12, False,
     {"durations_ms": [140, 80, 120]}),
    ("hurt", [flash(frame("mid")), frame("mid", 0, -1)], 12, False, {"durations_ms": [80, 120]}),
    ("death", [flash(frame("folded")), frame("folded", 2), frame("folded", 5), frame("folded", 8)], 10, False,
     {"durations_ms": [80, 90, 90, 260]}),
]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=False)
    print(f"strip: {HERE / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
