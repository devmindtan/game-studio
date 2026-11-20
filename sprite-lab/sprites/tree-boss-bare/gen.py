#!/usr/bin/env python3
"""Generator cho "tree-boss-bare": Cổ Thụ Trụi Lá, Mộc Yêu pha 2 (Bách Ải design/bosses.md, người dùng 2026-11-19).

Nâng cấp từ tree-boss đã duyệt (không vẽ lại): cùng thân, mặt, cành tay, cùng khung 48x48 và neo; tán lá rụng sạch để
lộ ngọn cành khô và lõi tinh thể xanh ngọc phát sáng (nhấp nháy theo nhịp bước); bộ rễ cuộn thành hai chân rễ thô
có đầu gối mấu, ngón rễ cuộn, chạy theo chu kỳ 8 khung. game đổi sang sheet này khi boss vào pha 2
(monsters.json rage_sprite, Enemies.sheet_of).
Chạy: gamekit art run tree-boss-bare
"""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("tree_gen", HERE.parent / "tree-boss" / "gen.py")
tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tree)

if __name__ == "__main__":
    tree.BARE = True   # same frames, built in phase 2 dress
    tree.export(HERE, "tree-boss-bare", tree.build(), anchor=tree.ANCHOR, ground=True, body="move",
                preview_scale=6, gif_scale=4)
    print("OK tree-boss-bare")
