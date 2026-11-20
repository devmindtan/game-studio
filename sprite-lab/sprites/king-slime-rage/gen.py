#!/usr/bin/env python3
"""Generator cho "king-slime-rage": Vua Thạch Nhầy khi phẫn nộ (thân đỏ).

Người dùng 2026-11-19: máu xuống mức cố định (rage_at) thì nội tại phẫn nộ kích hoạt, thân chuyển đỏ và ra
chiêu nhanh hơn. Nhuộm màu không biến xanh thành đỏ được, nên đây là cùng mọi khung của king-slime vẽ bằng
RAGE_PAL, mắt luôn cau và có dấu tức giận đỏ nhấp nháy cạnh đầu; game đổi sang sheet này khi boss phẫn nộ (monsters.json rage_sprite, Enemies.sheet_of).
Chạy: gamekit art run king-slime-rage
"""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("king_gen", HERE.parent / "king-slime" / "gen.py")
king = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(king)

def transform():
    """Green -> enraged red (user 2026-11-20: the bosses lacked a change animation), 12 frames over ~1.5 s
    played by the game during the transition: it quivers, flushes from green to red in steps, its eyes narrow
    into a scowl, it swells up tall and the anger mark bursts out beside its crown."""
    green, red = king.PAL, king.RAGE_PAL
    steps = [("normal", 0.0, "open", 0, False), ("squash", 0.1, "open", 1, False), ("stretch", 0.2, "open", -1, False),
             ("squash", 0.3, "closed", 2, False), ("stretch", 0.4, "angry", -1, False), ("squash", 0.5, "angry", 1, False),
             ("stretch", 0.6, "angry", -2, False), ("squash", 0.7, "angry", 2, False), ("flat", 0.8, "angry", 2, False),
             ("stretch", 0.9, "angry", -3, True), ("stretch", 1.0, "angry", -3, True), ("normal", 1.0, "angry", 0, True)]
    frames = []
    for n, (sh, t, eyes, cdy, mark) in enumerate(steps):
        king.RAGE = mark
        # flickers green / red, red more and more often (a blend passes through a muddy brown)
        pal = red if n in (2, 4, 6, 7) or n >= 9 else green
        c = king.shape(sh, eyes=eyes, crown_dy=cdy, pal=pal, bubble=n, dx=(1 if n % 2 and n < 9 else 0))
        frames.append(king.flash(c, 0.6) if n == 8 else c)   # the deepest strain flashes white
    king.RAGE = True
    return ("transform", frames, 8, False, {"durations_ms": [100, 100, 110, 110, 120, 120, 120, 130, 160, 120, 140, 250],
                                            "hitbox": {**king.HB, "active": [0, 11]}})


if __name__ == "__main__":
    tf = transform()
    king.PAL = king.RAGE_PAL
    king.RAGE = True   # always angry, with the anger mark
    import json   # same frames and descriptions as king-slime, plus the transform
    brief = json.load(open(HERE.parent / "king-slime" / "brief.json"))
    brief["frames"]["transform"] = ["tròn, xanh, bắt đầu run", "bẹp, xanh", "vươn, nháy đỏ", "bẹp, nhắm mắt gồng (xanh)",
        "vươn, mắt cau, nháy đỏ", "bẹp, xanh", "vươn, đỏ", "bẹp, đỏ", "dẹt, gồng sâu nhất, chớp trắng",
        "vươn cao, đỏ, dấu giận bật ra", "vươn cao nhất, đỏ rực", "về tròn, phẫn nộ (vào pha 2)"]
    json.dump(brief, open(HERE / "brief.json", "w"), ensure_ascii=False, indent=2)
    king.export(HERE, "king-slime-rage", king.build() + [tf], anchor=king.ANCHOR, ground=True, body="move",
                preview_scale=5, gif_scale=3)
    print("OK king-slime-rage")
