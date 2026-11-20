#!/usr/bin/env python3
"""Generator cho "toad-king-spore": Cóc Độc Bào Tử, Cóc Chúa pha 2 (Bách Ải design/bosses.md, người dùng 2026-11-19).

Nâng cấp từ toad-king đã duyệt (không vẽ lại): cùng dáng, cùng khung 56x48 và neo; cụm nấm trên lưng phình to
(x1.45), tím rực, có đốm và liên tục nhả khói bào tử (các hạt bào tử bay lên qua từng khung); các nốt sần hai bên đỏ
rực, phập phồng sáng / tối luân phiên như sắp nổ. attack há miệng không có cục độc (pha 2 phóng lưỡi, không phun). Cùng animation và mô tả khung với toad-king. game đổi sang sheet
này khi boss vào pha 2 (monsters.json rage_sprite, Enemies.sheet_of).
Chạy: gamekit art run toad-king-spore
"""

import importlib.util
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("toad_king_gen", HERE.parent / "toad-king" / "gen.py")
king = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(king)

if __name__ == "__main__":
    king.SPORE = True
    king.toadkit.CROWN_GROW = 1.45
    king.toadkit.CROWN_GLOW = True
    king.toadkit.NO_GLOB = True   # attack = the open mouth the tongue shoots from, no spit
    shutil.copy(HERE.parent / "toad-king" / "brief.json", HERE / "brief.json")   # same frames, same descriptions
    king.export(HERE, "toad-king-spore", king.build(), anchor=king.ANCHOR, ground=True, body="move",
                preview_scale=5, gif_scale=3)
    print("OK toad-king-spore")
