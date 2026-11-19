#!/usr/bin/env python3
"""Generator cho "king-slime-rage": Vua Thạch Nhầy khi phẫn nộ (thân đỏ).

Người dùng 2026-11-19: máu xuống mức cố định (rage_at) thì nội tại phẫn nộ kích hoạt, thân chuyển đỏ và ra
chiêu nhanh hơn. Nhuộm màu không biến xanh thành đỏ được, nên đây là cùng mọi khung của king-slime vẽ bằng
RAGE_PAL; game đổi sang sheet này khi boss phẫn nộ (monsters.json rage_sprite, Enemies.sheet_of).
Chạy: gamekit art run king-slime-rage
"""

import importlib.util
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("king_gen", HERE.parent / "king-slime" / "gen.py")
king = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(king)

if __name__ == "__main__":
    king.PAL = king.RAGE_PAL
    shutil.copy(HERE.parent / "king-slime" / "brief.json", HERE / "brief.json")   # same frames, same descriptions
    king.export(HERE, "king-slime-rage", king.build(), anchor=king.ANCHOR, ground=True, body="move",
                preview_scale=5, gif_scale=3)
    print("OK king-slime-rage")
