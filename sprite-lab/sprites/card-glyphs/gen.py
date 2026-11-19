#!/usr/bin/env python3
"""Generator cho "card-glyphs": ký hiệu thay đổi ghép vào góc icon nút cây thẻ (Bách Ải, design/skill-tree-v2.md §5).

Icon nút = icon thẻ gốc + một ký hiệu ở góc: damage (kiếm), area (vòng), cooldown (đồng hồ cát), count (×2),
bleed (giọt máu), burn (lửa), shock (tia sét), stun (sao), slow (ốc / mũi tên chậm), freeze (bông tuyết), và
"shard" (Mảnh thẻ, tiền tệ). Mỗi ký hiệu một animation một khung 12x12, nền trong, viền tối 1 px để đọc trên mọi icon.
Chạy: gamekit art run card-glyphs
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

NAME = "card-glyphs"
SIZE = 12
OUTLINE = "#14101c"
PAL = {"w": "#ffffff", "s": "#c8d0e0", "g": "#ffd04a", "G": "#c8902a", "r": "#e8364a", "R": "#a01828",
       "o": "#ff8a2a", "y": "#ffe070", "b": "#7ad0ff", "B": "#3a7ad0", "c": "#d8f4ff", "p": "#c070ff", "P": "#7a3ab0",
       "n": "#8a6a4a"}
GLYPHS = {
    "damage": ["........ss", ".......sws", "......sws.", ".....sws..", "..g.sws...", "...gws....", "...Gg.....", "..G..g....", ".G........", "G........."],
    "area": ["...bbbb...", "..b....b..", ".b..BB..b.", "b..B..B..b", "b..B.wB..b", "b..B..B..b", ".b..BB..b.", "..b....b..", "...bbbb...", ".........."],
    "cooldown": ["gggggggg", ".nyyyyn.", "..nyyn..", "...yy...", "...ny...", "..n..n..", ".n.yy.n.", "nyyyyyyn", "gggggggg"],
    "count": ["w.....w...", ".w...w....", "..w.w.....", "...w....rr", "..w.w..r..r", ".w...w...r.", "w.....w.r..", "........rrrr"],
    "bleed": ["...r....", "...r....", "..rRr...", ".rRRRr..", "rRRwRRr.", "rRRRRRr.", ".rRRRr..", "..rrr..."],
    "burn": ["...o....", "..oo..o.", ".ooy.oo.", ".oyyooo.", "ooyyyoo.", "oyywyyo.", "oyyyyyo.", ".ooooo.."],
    "shock": ["....yyy", "...yyy.", "..yyy..", ".yyyyyy", "...yyy.", "..yy...", ".yy....", "yy....."],
    "stun": ["..y...y..", "...y.y...", ".yyywyyy.", "...y.y...", "..y...y..", "........."],
    "slow": ["....cc....", ".c..cc..c.", "..c.cc.c..", "...cccc...", "ccccwwcccc", "...cccc...", "..c.cc.c..", ".c..cc..c.", "....cc...."],
    "freeze": ["...bb...", "..bccb..", ".bccccb.", "bccwwccb", "bccwwccb", ".bccccb.", "..bccb..", "...bb..."],
    "shard": ["...p....", "..ppp...", ".pPwpp..", "pPPpppp.", ".pPPpp..", "..pPp...", "...p...."],
}


def glyph(rows):
    w = max(len(r) for r in rows)
    art = from_rows([r.ljust(w, ".") for r in rows], PAL)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, (SIZE - art.height) // 2)
    return c.outline(OUTLINE)


ANIMATIONS = [(name, [glyph(rows)], 1, True, {}) for name, rows in GLYPHS.items()]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(6.0, 6.0), ground=False, preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
