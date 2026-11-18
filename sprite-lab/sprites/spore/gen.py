#!/usr/bin/env python3
"""Generator cho sprite "spore" (Nấm Phun): quái bắn xa của vùng Đồng cỏ (Bách Ải, đợt 6A).

Cây nấm độc biết đi: mũ đỏ chấm trắng, thân kem, hai chân ngắn. Nó giữ khoảng cách với người chơi và
phồng mũ phun một cục bào tử (đạn: sprite "spore-bolt"). Silhouette khác hẳn thạch nhầy / dơi / yêu tinh:
mũ to rộng trên thân hẹp, đọc được ở 1x.
Frame 24x24, quay phải, neo (12, 23) giữa đáy (ground=True). Animation: move 4 (lạch bạch), attack 3
(nén mũ → phồng → phun, frame 2 là lúc bắn), hurt 2 (nháy trắng), death 4 (mũ sụp, tan thành bụi).
Chạy: gamekit art run spore
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

NAME = "spore"
SIZE = 24
ANCHOR = (12.0, 23.0)
OUTLINE = "#1b1726"
PAL = {
    "r": "#c8323c", "R": "#8a1f30", "o": "#ee6a5a",   # cap: red, shade, light
    "w": "#fff2dc",                                   # cap spots
    "s": "#efe0c0", "S": "#c2a882",                   # stem: cream, shade
    "e": "#1b1726",                                   # eye
    "g": "#9ad85a", "G": "#5e9a30",                   # spore puff (green)
    "f": "#8a6a4a",                                   # feet
}

CAP = {
    "normal": [
        ".....rrrrrr.....",
        "...rroowrrrrr...",
        "..rrowwrrrwwrr..",
        ".rrorrrrrrrwwrr.",
        ".rrrrwwrrrrrrrR.",
        "RRrrrwwrrrrrrRRR",
        ".RRRRRRRRRRRRRR.",
    ],
    "squash": [
        "....rrrrrrrr....",
        "..rroowrrrrrrr..",
        ".rrowwrrrrrwwrr.",
        "RRrrrrwwrrrrrRRR",
        ".RRRRRRRRRRRRRR.",
    ],
    "puff": [
        "......rrrr......",
        "....rroowrrr....",
        "...rowwrrrwwr...",
        "..rrorrrrrrwwr..",
        "..rrrrwwrrrrrR..",
        ".RRrrrwwrrrrRRR.",
        "..RRRRRRRRRRRR..",
    ],
}

STEM = [
    "....ssssss....",
    "....sesses....",
    "....ssssSS....",
    "....sssSSS....",
    "...ssssSSSS...",
]
FEET = {0: ["...ff....ff...", "..fff...fff..."], 1: ["....ff..ff....", "...fff.fff...."],
        2: ["..ff......ff..", ".fff.....fff.."]}


def figure(cap="normal", feet=0, lift=0, puff=0, closed=False):
    stem = [r.replace("e", "s") for r in STEM] if closed else STEM
    rows = [r.center(16, ".") for r in CAP[cap]] + [r.center(16, ".") for r in stem] + \
           [r.center(16, ".") for r in FEET[feet]]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, 21 - (art.height - 1) - lift)
    if puff:   # a green spore cloud blown from the cap's front
        cloud = from_rows(["..gg..", ".gGgg.", "gggGg.", ".gggg.", "..g..."][:2 + puff], PAL)
        c.paste(cloud, 16, 21 - (art.height - 1) - lift - 1)
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


def dust(n):
    """Death: the cap collapses onto the stem, then a puff of spores."""
    if n == 0:
        return figure("squash", 2, closed=True)
    rows = {1: ["..RrrrrrrrrR..", ".RRrrwwrrrrRR.", "..ssssSSSSs..."],
            2: ["...g..g..g....", ".g..RrrrrR..g.", "..gggggggggg.."],
            3: ["..g.......g...", "....g...g.....", ".g....g....g.."]}[n]
    art = from_rows([r.center(16, ".") for r in rows], PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, 21 - (art.height - 1))
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [12.0, 23.0]}
ANIMATIONS = [
    ("move", [figure("normal", 0), figure("normal", 1), figure("normal", 2), figure("normal", 1)],
     8, True, {"durations_ms": [130, 110, 130, 110], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [figure("squash", 2), figure("puff", 0), figure("normal", 0, puff=3)], 10, False,
     {"durations_ms": [220, 160, 200], "hitbox": {**HB, "active": [0, 2]}}),
    ("hurt", [flash(figure("squash", 0, closed=True)), figure("normal", 0, closed=True)], 12, False,
     {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [dust(0), dust(1), dust(2), dust(3)], 8, False,
     {"durations_ms": [90, 120, 160, 260], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
