#!/usr/bin/env python3
"""Generator cho "leaf-bolt": lá úa của Cổ Thụ Trụi Lá (Mộc Yêu pha 2, games/bach-ai design/bosses.md):
tán rụng sạch thành Bão lá rụng bay tỏa tròn.

12x12, neo (6, 6) = tâm (vật bay). fly 4: chiếc lá xoay (thẳng → nghiêng → ngang → nghiêng), có gân lá; pop 3:
vụn lá tan. Vàng cam lá úa + viền tối để nổi trên cỏ tối và đất nâu của Rừng Âm U (khác đạn xanh của Nấm Phun).
Chạy: gamekit art run leaf-bolt
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

NAME = "leaf-bolt"
SIZE = 12
OUTLINE = "#1b1726"
PAL = {"g": "#f0a830", "G": "#b8641c", "l": "#ffe08a", "p": "#7a3a10"}

FLY = [   # p = the leaf's vein and stem
    ["...g...", "..glg..", ".gglGg.", ".glpGG.", ".gGpGG.", "..GpG..", "...p..."],
    ["....gg.", "..gglg.", ".gglpG.", ".glpGG.", "gGpGG..", "pGG....", "......."],
    [".......", ".ggg...", "glllgg.", "ppppppp", "gGGGGG.", ".GGG...", "......."],
    ["p......", ".gGg...", ".glpG..", "..gpGG.", "..glpG.", "...gGg.", "....gg."],
]
POP = [
    ["g..l..g", ".g.p.G.", "..gGg..", ".G.p.g.", "g..G..g"],
    ["g.....l", "..p....", ".....G.", "..g....", "G.....g"],
    ["l......", "...p...", ".......", "....g..", "......G"],
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
