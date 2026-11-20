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

def transform():
    """Phase 1 -> 2 (user 2026-11-20: the bosses lacked a change animation), 12 frames over ~1.5 s, played by
    the game during the invulnerable transition: it shudders, the canopy bursts into flying leaves, the jade
    core blazes out of the bare crown, the roots draw in and curl into the two legs, it rears up and roars.
    Refs: Hollow Knight style stun -> transition -> phase 2 (ludonauta devlog); boss packs give the
    'enter second phase' its own animation."""
    f = []
    tree.BARE, tree.CROWN, tree.LEGS = False, False, False
    f.append(tree.tree(2, 0, 0, 1, glow=True))                          # 0 shudders, eyes blaze
    f.append(tree.tree(-2, 0.5, 1, 0, glow=True, mouth=1))              # 1 shudders the other way, growls
    f.append(tree.tree(2, 0.5, 2, 1, glow=True, mouth=2))               # 2 canopy shaking hard
    f.append(tree.tree(0, 1, 0, -1, glow=True, mouth=2, shed=0.35))     # 3 the canopy tears, leaves burst
    f.append(tree.tree(0, 1, 0, -1, glow=True, mouth=3, shed=0.7))      # 4 more leaves fly
    tree.CROWN = True
    f.append(tree.tree(0, 1, 0, -2, glow=True, mouth=3))                # 5 bare crown: the jade core blazes
    f.append(tree.tree(0, 1, 2, -2, glow=True, mouth=3))                # 6 the core flares again
    tree.CURL = 3
    f.append(tree.tree(0, 0.5, 0, 0, glow=True, mouth=2))               # 7 the roots draw in, tips up
    tree.CURL = 5
    f.append(tree.tree(0, 0.5, 0, 1, glow=True, mouth=2))               # 8 curled tight
    tree.CURL = 0
    tree.LEGS = True
    f.append(tree.tree(0, 0, 2, 3, glow=True, mouth=2))                 # 9 the legs plant, crouched low
    f.append(tree.tree(0, 1, 0, -1, glow=True, mouth=3))                # 10 rises on them, arms up
    f.append(tree.tree(0, 1, 4, -3, glow=True, mouth=4))                # 11 rears up and roars
    tree.BARE, tree.CROWN, tree.LEGS = True, None, None
    return ("transform", f, 8, False, {"durations_ms": [100, 100, 110, 130, 130, 130, 120, 120, 120, 140, 140, 260],
                                        "hitbox": {**tree.HB, "active": [0, 11]}})


if __name__ == "__main__":
    tree.BARE = True   # same frames, built in phase 2 dress
    tree.export(HERE, "tree-boss-bare", tree.build() + [transform()], anchor=tree.ANCHOR, ground=True, body="move",
                preview_scale=6, gif_scale=4)
    print("OK tree-boss-bare")
