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

def _mix(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02x" % round(x + (y - x) * t) for x, y in zip(ca, cb))


def transform():
    """Phase 1 -> 2 (user 2026-11-20: the bosses lacked a change animation), 12 frames over ~1.5 s, played by
    the game during the invulnerable transition: the toad trembles, its warts redden and throb, the crown
    swells step by step, turns glowing purple and bursts in a cloud of spores, then it rears and bellows.
    Refs: stun -> transition -> phase 2 (ludonauta devlog, Hollow Knight style)."""
    P = king.P
    tk = king.toadkit
    base = dict(king.KPAL)
    frames = []
    steps = [  # (pose, red 0..1, crown grow, glow, burst, mouth)
        ("sit", 0.0, 1.0, False, 0, 0), ("sit_low", 0.15, 1.0, False, 0, 0), ("sit_puff", 0.3, 1.05, False, 0, 0),
        ("sit_low", 0.45, 1.12, False, 0, 0), ("sit_puff", 0.6, 1.2, False, 0, 0), ("sit_low", 0.75, 1.28, False, 0, 0),
        ("sit_puff", 0.9, 1.36, True, 0, 0), ("crouch", 1.0, 1.45, True, 1, 0), ("crouch_deep", 1.0, 1.45, True, 2, 0),
        ("crouch", 1.0, 1.45, True, 3, 0.4), ("sit", 1.0, 1.45, True, 2, 0.9), ("sit", 1.0, 1.45, True, 1, 1.0)]
    for n, (pose, red, grow, glow, burst, mouth) in enumerate(steps):
        king.SPORE = False
        king.KPAL = {**base, **{k: _mix(base[k], v, red) for k, v in king.SPORE_PAL.items()}}
        tk.CROWN_GROW, tk.CROWN_GLOW, tk.SPORE_PHASE, tk.NO_GLOB = grow, glow, n, True
        extra = {"mouth": mouth} if mouth else {}
        if n in (1, 3):   # squeezes its eyes shut as it strains
            extra["eyes"] = "shut"
        c = king.frame(pose, **extra)
        if burst:   # the spore cloud bursting off the crown
            px = c.img.load()
            import math
            for k in range(10 + 6 * burst):
                a = k / (10 + 6 * burst) * 2 * math.pi
                r = 6 + burst * 5 + (k % 3)
                x, y = round(22 + math.cos(a) * r), round(12 + math.sin(a) * r * 0.7)
                if 0 <= x < c.width and 0 <= y < c.height and px[x, y][3] == 0:
                    px[x, y] = (240, 200, 255, 255) if k % 2 else (192, 96, 255, 255)
        frames.append(c)
    king.KPAL = base
    king.SPORE = True
    return ("transform", frames, 8, False, {"durations_ms": [100, 100, 110, 110, 120, 120, 130, 130, 140, 140, 160, 240],
                                            "hitbox": {**king.HB, "active": [0, 11]}})


if __name__ == "__main__":
    king.toadkit.NO_GLOB = True
    tf = transform()
    king.SPORE = True
    king.toadkit.CROWN_GROW = 1.45
    king.toadkit.CROWN_GLOW = True
    king.toadkit.NO_GLOB = True   # attack = the open mouth the tongue shoots from, no spit
    import json   # same frames and descriptions as toad-king, plus the transform
    brief = json.load(open(HERE.parent / "toad-king" / "brief.json"))
    brief["frames"]["transform"] = ["ngồi, bắt đầu run", "co mình, nhắm mắt, mụn ửng đỏ", "họng phập phồng, nấm nhú to",
        "co mình, nhắm mắt, mụn đỏ hơn", "phồng họng, nấm to thêm", "co mình, mụn gần đỏ hẳn", "nấm hóa tím rực, phát sáng",
        "gồng xuống, bào tử bắt đầu tung", "gồng sâu nhất, đám bào tử nổ lớn", "bật lên, há miệng", "ngồi dậy, gầm",
        "gầm lớn, bào tử lắng (vào pha 2)"]
    json.dump(brief, open(HERE / "brief.json", "w"), ensure_ascii=False, indent=2)
    king.export(HERE, "toad-king-spore", king.build() + [tf], anchor=king.ANCHOR, ground=True, body="move",
                preview_scale=5, gif_scale=3)
    print("OK toad-king-spore")
