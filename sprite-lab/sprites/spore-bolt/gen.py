#!/usr/bin/env python3
"""Generator cho "spore-bolt": cục bào tử độc Nấm Phun bắn ra (đạn của quái, đợt 6A).

12x12, neo (6, 6) = tâm (vật bay). Animation fly 4: cục xanh độc xoay và đập nhẹ, vệt đuôi nhạt; pop 3:
vỡ tung khi chạm hoặc hết tầm. Màu xanh độc + viền tối để nổi trên nền cỏ (khác đạn phép xanh lam của người
chơi). Chạy: gamekit art run spore-bolt
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

NAME = "spore-bolt"
SIZE = 12
OUTLINE = "#1b1726"
PAL = {"g": "#9ad85a", "G": "#5e9a30", "l": "#e2ffb0", "p": "#b04ad8"}

FLY = [
    ["..gGg..", ".glggG.", "gllggGG", "gggggGG", ".ggGGG.", "..GGG.."],
    ["..ggg..", ".gllgG.", "gllggGG", "ggpggGG", ".ggGGG.", "..GGG.."],
    ["..gGg..", ".ggllG.", "ggllgGG", "gggggGG", ".gGGGG.", "..GGG.."],
    ["..ggg..", ".glggG.", "gllgpGG", "gggggGG", ".ggGGG.", "..GGG.."],
]
POP = [
    ["g..g..g", ".gllgG.", "glpggGg", ".ggGGG.", "g..G..g"],
    ["g.....g", "..l.g..", ".g...G.", "..g.G..", "g.....g"],
    ["l.....g", ".......", "...p...", ".......", "g.....l"],
]


def frame(rows):
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, (SIZE - art.height) // 2)
    return c.outline(OUTLINE)


ANIMATIONS = [
    ("fly", [frame(r) for r in FLY], 10, True, {"hitbox": {"shape": "circle", "center": [6.0, 6.0], "active": [0, 3]}}),
    ("pop", [frame(r) for r in POP], 14, False, {}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(6.0, 6.0), preview_scale=8, gif_scale=8)
    print(f"OK {NAME}")
