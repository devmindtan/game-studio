#!/usr/bin/env python3
"""Generator cho sprite "ui-icons": bộ icon giao diện 16x16 (Bách Ải), vẽ tay bằng bản đồ pixel.

Mỗi icon là một animation 1 frame, tên = vai trò: heart (máu), skull (số mạng đã hạ), coin (vàng),
gem (kinh nghiệm), star (cấp), clock (thời gian), sword (sát thương), boot (tốc độ chạy),
và 12 icon thẻ nâng cấp với tên trùng upgrade id: blade_arc, back_slash, whirlwind, sharpen,
haste, reach, vitality, swift, magnet, regen, frost_nova, earth_strike; Đợt 2: ground_slam,
cleave_wave, holy_column, dash, toughness.
Viền tối 1 px như mọi sprite; neo (8, 8) = tâm ô. Game vẽ bằng SpriteSheet theo tên animation.
Chạy: gamekit art run ui-icons
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas, from_rows  # noqa: E402
from sheet import export  # noqa: E402

NAME = "ui-icons"
SIZE = 16
OUTLINE = "#1b1726"

ICONS = {
    "heart": ({"r": "#d9364a", "l": "#ff8a8a", "w": "#ffffff", "d": "#8f1f35"}, [
        "..rrr...rrr..",
        ".rlwrr.rrrrr.",
        "rlwlrrrrrrrrd",
        "rllrrrrrrrrrd",
        "rrrrrrrrrrrrd",
        ".rrrrrrrrrrd.",
        "..rrrrrrrrd..",
        "...rrrrrrd...",
        "....rrrrd....",
        ".....rrd.....",
        "......d......",
    ]),
    "skull": ({"w": "#f2ecd8", "g": "#b9b2a0", "k": "#1b1726"}, [
        "...wwwwwww...",
        "..wwwwwwwwwg.",
        ".wwwwwwwwwwwg",
        ".wkkkwwwkkkwg",
        ".wkkkwwwkkkwg",
        ".wwkwwkwwkwwg",
        "..wwwwkwwwwg.",
        "...wwwwwwwg..",
        "...wkwkwkwg..",
        "....g.g.g....",
    ]),
    "coin": ({"o": "#a8661f", "y": "#f2c14e", "l": "#fff2a8", "m": "#d9952b"}, [
        "...oooooo...",
        "..oyyyyyyo..",
        ".oyllyyyyyo.",
        "oyllyymyyyyo",
        "oylyymmmyyyo",
        "oyyyyymyyyyo",
        "oyyyymmmyyyo",
        "oyyyyymyyyyo",
        ".oyyyyyyyyo.",
        "..oyyyyyyo..",
        "...oooooo...",
    ]),
    "gem": ({"b": "#4fa3e0", "l": "#bfe6ff", "w": "#ffffff", "d": "#2c5a8c"}, [
        "....bbb....",
        "...blwbb...",
        "..bllbbbb..",
        ".bllbbbbbb.",
        "blbbbbbbbbd",
        ".bbbbbbbbd.",
        "..bbbbbbd..",
        "...bbbbd...",
        "....bbd....",
        ".....d.....",
    ]),
    "star": ({"y": "#f2c14e", "l": "#fff2a8", "o": "#c9852b"}, [
        "......y......",
        ".....yly.....",
        ".....yly.....",
        "yyyyyylyyyyyy",
        ".yyylyyyyyyo.",
        "..yyyyyyyyo..",
        "...yyyyyyo...",
        "..yyyyoyyyo..",
        "..yyyo.oyyo..",
        ".yyo.....oyo.",
        ".yo.......oo.",
    ]),
    "clock": ({"r": "#6b4a2b", "w": "#f2ecd8", "g": "#b9b2a0", "k": "#1b1726"}, [
        "...rrrrrrr...",
        "..rwwwwwwwr..",
        ".rwwwwkwwwgr.",
        "rwwwwwkwwwwgr",
        "rwwwwwkwwwwgr",
        "rwwwwwkkkwwgr",
        "rwwwwwwwwwwgr",
        "rwwwwwwwwwwgr",
        ".rwwwwwwwwgr.",
        "..rggggggr...",
        "...rrrrrrr...",
    ]),
    "sword": ({"w": "#e8f0f6", "s": "#9fb3c8", "g": "#e8b84a", "b": "#6b4a2b"}, [
        "...........ws",
        "..........wws",
        ".........wws.",
        "........wws..",
        ".......wws...",
        "......wws....",
        "..g..wws.....",
        "...gwws......",
        "....gs.......",
        "...bggg......",
        "..bb..g......",
        ".bb..........",
    ]),
    "boot": ({"b": "#8a5a36", "l": "#b57d4f", "d": "#5a3a26", "s": "#3e2819", "w": "#9fd7ff"}, [
        "....bbbbb....",
        "....blbbb....",
        "....blbbb....",
        "w...blbbb....",
        ".w..blbbbbb..",
        "w...bbbbbbbb.",
        "...bbbbbbbbbb",
        "..ddddddddddd",
        "..sssssssssss",
    ]),

    # --- thẻ nâng cấp (tên = upgrade id trong assets/data/upgrades_*.json) ---
    "blade_arc": ({"w": "#e8f0f6", "s": "#9fb3c8"}, [
        "........www..",
        "......wwwss..",
        ".....wws.....",
        "....wws......",
        "...wws.......",
        "...wws.......",
        "....wws......",
        ".....wws.....",
        "......wwwss..",
        "........www..",
    ]),
    "back_slash": ({"w": "#e8f0f6", "s": "#9fb3c8", "g": "#e8b84a"}, [
        "..g......g...",
        "...ww....ww..",
        "...ww....ww..",
        "....ww..ww...",
        ".....wwww....",
        ".....wwww....",
        "....ww..ww...",
        "...ww....ww..",
        "...ww....ww..",
        "..g......g...",
    ]),
    "whirlwind": ({"w": "#d9e6f2", "s": "#7ea8c8"}, [
        "....wwwwww...",
        "..ww......ww.",
        ".w..wwwwww..w",
        ".w.ww....ww.w",
        ".w.ww.wwww..w",
        ".w..ww....w..",
        "..w..wwww.w..",
        "...ww....ww..",
        "....wwwwww...",
    ]),
    "sharpen": ({"w": "#e8f0f6", "s": "#9fb3c8", "g": "#8a8a96", "y": "#ffd36b"}, [
        "..........ww.",
        ".........wwws",
        "........wwws.",
        ".......wwws..",
        "......wwws...",
        "..g...wwws...",
        ".ggg.wwws....",
        "..gg.wws.....",
        ".....yy......",
        "....y..y.....",
        ".....yy......",
    ]),
    "haste": ({"w": "#e8dfc8", "s": "#f2c14e"}, [
        "...wwwwwwww...",
        "...wssssssw...",
        "....wssssw....",
        ".....wssw.....",
        "......ww......",
        "......ww......",
        ".....w..w.....",
        "....w....w....",
        "...w......w...",
        "...wwwwwwww...",
    ]),
    "reach": ({"w": "#e8f0f6", "s": "#9fb3c8", "g": "#e8b84a"}, [
        "............w.",
        "...........www",
        "..........wwww",
        ".........wwwww",
        "........wwww..",
        ".......wwww...",
        "......wwww....",
        ".....wwww.....",
        "....wwww......",
        "...wwww.......",
        "..gg..........",
    ]),
    "vitality": ({"r": "#d9364a", "l": "#ff8a8a", "w": "#ffffff", "d": "#8f1f35"}, [
        "...rr...rr...",
        "..rrrr.rrrr..",
        ".rrrrrrrrrrr.",
        ".rrrwwwwwrrr.",
        ".rrrwwwwwrrrd",
        ".rrrwwwwwrrrd",
        "..rrwwwwwrrd.",
        "...rrwwwrrd..",
        "....rrwrrd...",
        ".....rrrd....",
        "......rd.....",
    ]),
    "swift": ({"b": "#8a5a36", "d": "#5a3a26", "s": "#3e2819", "w": "#9fd7ff"}, [
        "..ww......ww..",
        ".wwww....wwww.",
        "..wwbbbbbbb...",
        "...wbbbbbbb...",
        "....bbbbbbb...",
        "....bbbbbbbb..",
        "...dddddddddd.",
        "...ssssssssss.",
    ]),
    "magnet": ({"r": "#d9364a", "b": "#4fa3e0", "d": "#8f1f35"}, [
        "..rr......bb..",
        ".rrrr....bbbb.",
        ".rrrr....bbbb.",
        ".rrrr....bbbb.",
        ".rrrr....bbbb.",
        ".rrrr....bbbb.",
        ".rrrrrrrrrrrr.",
        "..dddddddddd..",
    ]),
    "regen": ({"g": "#6ee06e", "w": "#d9ffe0", "d": "#2f7a45"}, [
        "....gggg....",
        "....gwwg....",
        "ggggwwwwgggg",
        "ggggwwwwgggg",
        "ggggwwwwgggg",
        "....gwwg....",
        "....gggg....",
    ]),
    "frost_nova": ({"w": "#dff6ff", "b": "#7ec8f0", "d": "#2c5a8c"}, [
        ".....ww.....",
        ".....ww.....",
        "..b..ww..b..",
        "...b.ww.b...",
        "....bbbb....",
        "bbbbwwwwbbbb",
        "....bbbb....",
        "...b.ww.b...",
        "..b..ww..b..",
        ".....ww.....",
        ".....ww.....",
    ]),
    "earth_strike": ({"b": "#c79a6a", "m": "#8a6a52", "d": "#5a4335", "r": "#ff6a2a"}, [
        "......b......",
        ".....bbb.....",
        "....bbbbb....",
        "....bmbmb....",
        "...bbmbmbb...",
        "...bbbbbbb...",
        "..bbbbbbbbb..",
        "..mmmmmmmmm..",
        "..ddddddddd..",
        "....rrrrr....",
    ]),
    # armour (giáp): a steel kite shield with a gold rim and a cross band
    "shield": ({"o": "#c9a65a", "s": "#9fb3c8", "l": "#e8f0f6", "d": "#5f7186", "c": "#3f7fbf"}, [
        "ooooooooooo",
        "olllssssddo",
        "olssscsssdo",
        "olssscsssdo",
        "occccccccco",
        "olssscsssdo",
        ".olsscssdo.",
        ".osssscsdo.",
        "..ossdsdo..",
        "...ossdo...",
        "....odo....",
        ".....o.....",
    ]),
    # ground_slam: a stone fist-arrow slamming into cracked ground
    "ground_slam": ({"a": "#e8c48a", "m": "#c79a6a", "b": "#ff9a3a", "d": "#5a4335"}, [
        "....aam....",
        "....aam....",
        "....aam....",
        "..aaaaamm..",
        "...aaamm...",
        "....amm....",
        ".....m.....",
        "b.b.....b.b",
        ".bb.ddd.bb.",
        "mmmddddddmm",
        "ddd.d.d.ddd",
    ]),
    # cleave_wave: a sword crescent flying right, with motion lines
    "cleave_wave": ({"w": "#e8f0f6", "l": "#6fc3ff", "g": "#9fb3c8"}, [
        "......www....",
        ".......wlw...",
        "........wlw..",
        "gg.......wlw.",
        ".........wlw.",
        "ggg......wlw.",
        ".........wlw.",
        "gg.......wlw.",
        "........wlw..",
        ".......wlw...",
        "......www....",
    ]),
    # holy_column: a golden beam striking down onto a glowing spot
    "holy_column": ({"y": "#ffe98a", "w": "#ffffff", "o": "#c9a65a"}, [
        "...yyyyy...",
        "....ywy....",
        "....ywy....",
        "....ywy....",
        "....ywy....",
        "....ywy....",
        "...yywyy...",
        "..y.ywy.y..",
        ".yyyyyyyyy.",
        "..ooooooo..",
    ]),
    # dash: a double chevron in the hero's scarf red, speed lines behind
    "dash": ({"r": "#d94a4a", "l": "#ff8a8a", "g": "#9fb3c8"}, [
        "...l...l.....",
        "...rl..rl....",
        "gg..rl..rl...",
        ".....rl..rl..",
        "ggg...rl..rl.",
        ".....rr..rr..",
        "gg..rr..rr...",
        "...rr..rr....",
        "...r...r.....",
    ]),
    # toughness: a steel breastplate (armour card)
    "toughness": ({"s": "#9fb3c8", "l": "#e8f0f6", "d": "#5f7186", "o": "#c9a65a"}, [
        ".ss.....ss.",
        "sllss.ssssd",
        "slsssosssdd",
        ".sssssssss.",
        ".slsssssssd",
        ".sssssssssd",
        "..slssssd..",
        "..ssssssd..",
        "...sssdd...",
        "....sdd....",
    ]),
    # settings: a steel gear with a hole
    "gear": ({"g": "#9fb3c8", "l": "#e8f0f6", "d": "#5f7186"}, [
        "....lll....",
        ".ll.lgl.ll.",
        ".lgggggggd.",
        "..ggggggg..",
        "lggg...gggd",
        "lggg...gggd",
        "lggg...gggd",
        "..ggggggd..",
        ".gggggggdd.",
        ".dd.ddd.dd.",
        "....ddd....",
    ]),
}


def icon(name):
    pal, rows = ICONS[name]
    art = from_rows(rows, pal)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, (SIZE - art.height) // 2)
    c.outline(OUTLINE)
    return c


ANIMATIONS = [(n, [icon(n)], 1, False, {}) for n in ICONS]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(8.0, 8.0), preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
