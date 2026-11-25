#!/usr/bin/env python3
"""Generator cho "gear-icons": 48 icon trang bị 24x24 của Bách Ải (2 class x 6 ô x 4 độ hiếm).

Mỗi ô của mỗi class có MỘT hình nền (BASE) vẽ tay bằng bản đồ pixel; độ hiếm cao hơn chồng thêm
chi tiết (OVER: sừng, cánh, ngọc, sao) và đổi bảng màu (PAL), để hình và màu cùng nói lên độ hiếm.
Chữ cái là vai trò màu, không phải màu: d tối, m giữa, l sáng, h điểm sáng (ánh sáng từ trên-trái),
t/T viền trang trí (thường: trùng màu chất liệu), k khe tối, b/B gỗ-da, c/C vải phụ, g/G ngọc,
n/N sừng, w/W cánh. Viền ngoài 1 px tự thêm (OUTLINE). Tên animation = id món trong items.json.
Tham khảo: design/equipment.md ("Bộ trang bị 6 ô").
Chạy: gamekit art run gear-icons
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

from PIL import Image, ImageDraw  # noqa: E402
from spritekit import Canvas, from_rows  # noqa: E402
from sheet import export  # noqa: E402

NAME = "gear-icons"
SIZE = 24
OUTLINE = "#1b1726"
RARITIES = ["common", "rare", "epic", "legendary"]
SLOTS = ["head", "chest", "legs", "arms", "feet", "weapon"]
CLASS_SLOTS = {"knight": ["head", "chest", "feet", "weapon", "shield"], "mage": ["head", "chest", "feet", "weapon"]}   # user 2026-11-25: knight set

# --- palettes: class -> rarity -> role letter -> colour -------------------------
_K = "#1b1726"
PAL = {
    "knight": {
        "common": {"d": "#4a4f5c", "m": "#7a808c", "l": "#a8aeb8", "h": "#d7dce2", "t": "#7a808c", "T": "#4a4f5c",
                   "k": _K, "b": "#6b4a2b", "B": "#4a321c", "g": "#8a3030", "G": "#c86a6a"},
        "rare": {"d": "#5f7186", "m": "#9fb3c8", "l": "#c9d6e2", "h": "#f2f7fb", "t": "#3f7fd0", "T": "#24508c",
                 "k": _K, "b": "#5a3a26", "B": "#3e2819", "g": "#37b9e8", "G": "#bfe6ff"},
        "epic": {"d": "#2e1b2e", "m": "#5a2f4f", "l": "#8a4a6e", "h": "#c27aa0", "t": "#c38df5", "T": "#7b4bb0",
                 "k": _K, "b": "#3e2819", "B": "#2a1a10", "g": "#ff4a6a", "G": "#ffb3c0", "n": "#e8d8b0", "N": "#a89870"},
        "legendary": {"d": "#8a5a1a", "m": "#d49a2a", "l": "#f2c14e", "h": "#fff2a8", "t": "#e8f0f6", "T": "#9fb3c8",
                      "k": "#3a2410", "b": "#6b2a8a", "B": "#3e1a52", "g": "#4fd0ff", "G": "#d8f6ff",
                      "w": "#ffffff", "W": "#c9d6e2"},
    },
    "mage": {
        "common": {"d": "#5a4632", "m": "#8a6e4e", "l": "#b8976a", "h": "#e0c89a", "t": "#8a6e4e", "T": "#5a4632",
                   "k": _K, "c": "#6e6e7e", "C": "#4a4a58", "b": "#6b4a2b", "B": "#4a321c", "g": "#6fd66a", "G": "#c8ffc0"},
        "rare": {"d": "#1f3a6e", "m": "#2f5fa8", "l": "#4f8ad8", "h": "#9cc8ff", "t": "#ffd04a", "T": "#b8862a",
                 "k": _K, "c": "#e8e2d0", "C": "#b9b2a0", "b": "#8a5a2e", "B": "#563418", "g": "#7ef0ff", "G": "#ffffff"},
        "epic": {"d": "#2a1648", "m": "#4a2a80", "l": "#6e48b0", "h": "#a07ae0", "t": "#c38df5", "T": "#7b4bb0",
                 "k": _K, "c": "#1b1030", "C": "#120a22", "b": "#3a2a4a", "B": "#241830", "g": "#e05aff", "G": "#ffc8ff"},
        "legendary": {"d": "#10203f", "m": "#1f3b70", "l": "#2f5aa0", "h": "#5a8ad0", "t": "#ffd04a", "T": "#b8862a",
                      "k": _K, "c": "#fff2a8", "C": "#d9a63a", "b": "#e8f0f6", "B": "#9fb3c8", "g": "#7ef0ff", "G": "#ffffff",
                      "w": "#ffffff", "W": "#c9d6e2"},
    },
}

# --- base silhouettes: 20 x 20, one per class and slot ---------------------------
BASE = {
    ("knight", "head"): [
        "....................",
        "....................",
        "....................",
        ".......mllllm.......",
        ".....mlhhllllmd.....",
        "....mlhllllllmmd....",
        "...mlhlllllllmmmd...",
        "...mllllllllmmmmd...",
        "..mlllllllllmmmmmd..",
        "..mtttttttttttttTd..",
        "..mlkkkkkmmkkkkkmd..",
        "..mlkkkkkmmkkkkkmd..",
        "..mllllllmmmmmmmmd..",
        "..mlllllkmmkmmmmmd..",
        "..mllllkmmmmkmmmmd..",
        "..mlllllkmmkmmmmdd..",
        "...mllllllmmmmmmd...",
        "...mmlllllmmmmmdd...",
        "....ddmmmmmmmmdd....",
        "....................",
    ],
    ("knight", "chest"): [
        "....................",
        "....................",
        "....................",
        "...mmmm......mmmm...",
        "..mllhlm....mlllmd..",
        ".mlhllllmmmmlllmmmd.",
        ".mlhlllllllmmmmmmmd.",
        ".mlltllllllmmmmmtmd.",
        "..mlTllllllmmmmmTd..",
        "..mllllllllmmmmmmd..",
        "...mllllllmmmmmmd...",
        "...mllllllmmmmmmd...",
        "...mlllllmmmmmmmd...",
        "...mtttttttttttTd...",
        "...mbbbbbbtTbbbbBd..",
        "...mlllllmmmmmmmd...",
        "....mllllmmmmmmd....",
        ".....ddmmmmmmdd.....",
        "....................",
        "....................",
    ],
    ("knight", "legs"): [
        "....................",
        "....................",
        "....................",
        "...mmmmmmmmmmmmmd...",
        "...mtttttttttttTd...",
        "...mllllllmmmmmmd...",
        "...mlhllllmmmmmmd...",
        "...mllllmd.mmmmmd...",
        "...mlhlmd...mlmmd...",
        "...mlllmd...mlmmd...",
        "..mlhllmmd.mllmmmd..",
        "..mtTmmmmd.mtTmmmd..",
        "..mlhllmmd.mllmmmd..",
        "...mlhlmd...mlmmd...",
        "...mllmmd...mlmmd...",
        "...mllmmd...mlmmd...",
        "...mlmmmd...mlmmd...",
        "..mlmmmmd...mlmmmd..",
        "..dddddd....dddddd..",
        "....................",
    ],
    ("knight", "arms"): [
        "....................",
        "....................",
        "..........mm........",
        ".........mlmm.mm....",
        "......mm.mlmmmlmm...",
        ".....mlmmmlmmmlmd...",
        ".....mlmmmlmmmlmd...",
        "..mm.mlmmmlmmmlmd...",
        ".mlmmmlmmmlmmmlmd...",
        ".mllmmmmmmmmmmmmd...",
        "..mllllllllmmmmmd...",
        "...mlhlllllmmmmd....",
        "....mlllllmmmmd.....",
        "....mtttttttttTd....",
        "....mlllllmmmmmd....",
        "....mlhllmmmmmmd....",
        "....mllllmmmmmmd....",
        "....ddmmmmmmmmdd....",
        "....................",
        "....................",
    ],
    ("knight", "feet"): [
        "....................",
        "....................",
        "....................",
        "......mmmmmm........",
        "......mlllmmd.......",
        "......mlhlmmd.......",
        "......mtttttT.......",
        "......mllmmmd.......",
        "......mlhlmmd.......",
        "......mllmmmd.......",
        "......mllmmmmd......",
        "......mlllmmmmmd....",
        ".....mllllmmmmmmmd..",
        ".....mlhlllmmmmmmmd.",
        ".....mlllllllmmmmmd.",
        ".....dddddddddddddd.",
        "....................",
        "....................",
        "....................",
        "....................",
    ],
    ("knight", "weapon"): [
        "....................",
        "....................",
        ".................hl.",
        "................hlm.",
        "...............hlm..",
        "..............hlm...",
        ".............hlm....",
        "............hlm.....",
        "...........hlm......",
        "..........hlm.......",
        ".........hlm........",
        ".....t..hlm.........",
        "......thlm..........",
        ".......tlm..........",
        "......b.tT..........",
        ".....b...T..........",
        "....bB..............",
        "...gB...............",
        "..gG................",
        "....................",
    ],
    ("mage", "head"): [
        "....................",
        "....................",
        "...........mm.......",
        "..........mlmd......",
        ".........mlmmd......",
        "........mlmmd.......",
        "........mlmmmd......",
        ".......mlhmmmd......",
        "......mlhlmmmmd.....",
        ".....mllhlmmmmd.....",
        ".....mllllmmmmmd....",
        "....mtttttttttTd....",
        "....mTTTTTTTTTTd....",
        "..mlllllllmmmmmmmd..",
        ".mllllllmmmmmmmmmmd.",
        "..ddddddddddddddd...",
        "....................",
        "....................",
        "....................",
        "....................",
    ],
    ("mage", "chest"): [
        "....................",
        "....................",
        "....................",
        ".....mmmm..mmmm.....",
        "....mlhllkkkmmmmd...",
        "...mlhllllkmmmmmmd..",
        "..mlhllllltmmmmmmmd.",
        ".mlhlllllltmmmmmmmmd",
        ".cllllllllltmmmmmmmC",
        ".Cmllllllltmmmmmmd.C",
        "..mllllllltmmmmmmd..",
        "..mtttttttttttttTd..",
        "..mllllllltmmmmmmd..",
        "..mlllllllltmmmmmmd.",
        ".mllllllllltmmmmmmmd",
        ".mllllllllltmmmmmmmd",
        ".cccccccccccccccccC.",
        ".CCCCCCCCCCCCCCCCCC.",
        "....................",
        "....................",
    ],
    ("mage", "legs"): [
        "....................",
        "....................",
        "....................",
        "....mmmmmmmmmmmm....",
        "....tttttttttttT....",
        "....mllllllmmmmmd...",
        "....mlhllllmmmmmd...",
        "...mlhlllmd.mmmmmd..",
        "...mlllllmd.mmmmmd..",
        "...mllllmd...mmmmd..",
        "..mllllmmd...mmmmmd.",
        "..mllllmmd...mmmmmd.",
        "..mlllmmmd...mlmmmd.",
        "..mllmmmd.....mmmmd.",
        "..ccccccd.....ccccC.",
        "..CCCCCC......CCCCC.",
        "....................",
        "....................",
        "....................",
        "....................",
    ],
    ("mage", "arms"): [
        "....................",
        "....................",
        "....................",
        "....................",
        "......mmmmmmmm......",
        ".....mlhllllmmmd....",
        "....mtttttttttTd....",
        "....mllllllmmmmd....",
        "....mlhlgGgmmmmd....",
        "....mlllgggmmmmd....",
        "....mllllllmmmmd....",
        "....mtttttttttTd....",
        ".....mllllllmmd.....",
        "......dddddddd......",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
    ],
    ("mage", "feet"): [
        "....................",
        "....................",
        "....................",
        "....................",
        "......mmmm..........",
        "......mlhmd.........",
        "......mllmd.........",
        "......tttTd.........",
        "......mlllmd........",
        ".....mlhllmmmd......",
        ".....mllllmmmmmd....",
        ".....mllllmmmmmmmd..",
        "......dddddddddddmm.",
        "................mm..",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
    ],
    ("mage", "weapon"): [
        "....................",
        "..............gGG...",
        ".............gGGGg..",
        ".............gGggg..",
        "..............ggg...",
        ".............t.t....",
        "............tbt.....",
        "...........bB.......",
        "..........bB........",
        ".........bB.........",
        "........bB..........",
        ".......bB...........",
        "......bB............",
        ".....bB.............",
        "....bB..............",
        "...bB...............",
        "..bB................",
        ".tT.................",
        "....................",
        "....................",
    ],
}

# --- overlays: rarity extras drawn over the base ({row: row string}) ----------------
OVER = {
    ("knight", "head", "epic"): {1: ".n................n.", 2: ".Nn..............nN.", 3: "..Nn............nN..",
                                 4: "...N............N...", 9: ".........gG........."},
    ("knight", "head", "legendary"): {3: "w..................w", 4: "Ww................wW", 5: "WWw..............wWW",
                                      6: ".WWw............wWW.", 7: "..WW............WW..", 1: ".........gG.........",
                                      2: "........gGGg........", 9: ".........gG........."},
    ("knight", "chest", "epic"): {2: "..n............n....", 3: "..N.............N...", 8: ".........gG.........",
                                  9: "........gggG........", 10: ".........gg........."},
    ("knight", "chest", "legendary"): {2: "..w..............w..", 3: ".wW..............Ww.", 7: ".........tt.........",
                                       8: "........tgGt........", 9: "........tggt........", 10: ".........tt........."},
    ("knight", "legs", "epic"): {10: ".n..............n...", 11: ".Nn.............nN.."},
    ("knight", "legs", "legendary"): {4: ".........gG.........", 10: ".w..............w...", 11: ".Ww.............wW.."},
    ("knight", "arms", "epic"): {1: "..........n.........", 2: ".........nNn........", 9: "......n.............",
                                 10: "........gG.........."},
    ("knight", "arms", "legendary"): {10: "........gG..........", 11: ".......gGGg.........", 13: "....mtgtttttgtTd...."},
    ("knight", "feet", "epic"): {3: ".....n..............", 4: ".....Nn.............", 12: "...................n"},
    ("knight", "feet", "legendary"): {3: "...w................", 4: "..wWw...............", 5: "...WW...............",
                                      6: "......mtgGttT......."},
    ("knight", "weapon", "epic"): {4: "................n...", 6: "..............n.....", 8: "............n.......",
                                   13: ".......gG..........."},
    ("knight", "weapon", "legendary"): {10: "...w.....hlm........", 11: "..wWt..hlm..........", 12: "...Wwthlm...........",
                                        13: ".......gG...........", 14: "......b.tTw.........", 15: ".....b...TWw........"},
    ("mage", "head", "epic"): {11: "....mtttgGtttTd.....", 6: "..........g.........", 9: "........G..........."},
    ("mage", "head", "legendary"): {1: "...G.........G......", 2: "..GgG..............G", 5: "........c...........",
                                    8: ".........c..........", 11: "....mtttgGtttTd.....", 12: "....mTcTTTTTcTTd...."},
    ("mage", "chest", "epic"): {6: ".........gG.........", 7: "........gGGg........", 13: "....g.........g....."},
    ("mage", "chest", "legendary"): {6: ".....c.........c....", 7: ".........gG.........", 8: "........gGGg........",
                                     12: "...c...........c....", 14: "......c.......c....."},
    ("mage", "legs", "epic"): {4: "....tttttgGttttT....", 11: "....g.........g....."},
    ("mage", "legs", "legendary"): {4: "....tttttgGttttT....", 7: "....c.........c.....", 11: ".....c.........c....",
                                    13: "...c............c..."},
    ("mage", "arms", "epic"): {3: "........g...........", 7: "....mlGllllmmmmd....", 10: "....mlllgggmmGmd...."},
    ("mage", "arms", "legendary"): {2: ".......G............", 3: "......GgG...........", 4: ".......G............",
                                    8: "....mlhgGGGgmmmd....", 9: "....mllgGGGgmmmd....", 10: "....mlllgggmmmmd...."},
    ("mage", "feet", "epic"): {12: "......ddddddddddgmm.", 9: "......g............."},
    ("mage", "feet", "legendary"): {3: ".....w..............", 4: "....wWw.............", 5: ".....WW.............",
                                    12: "......dddddddddddgG."},
    ("mage", "weapon", "epic"): {0: "..............g.....", 1: "............t.gGG.t.", 2: "............tgGGGgt.",
                                 3: ".............gGggg..", 4: "..............ggg..."},
    ("mage", "weapon", "legendary"): {0: "...............G....", 1: "............GgGGGgG.", 2: ".............gGGGg..",
                                      3: "............GgGGGgG.", 4: "...............g....", 9: ".........bB...c.....",
                                      7: ".....c.....bB......."},
}

# --- the 48 items: (class, slot, rarity) -> item id (items.json) ------------------
ITEMS = {
    ("knight", "head"): ["iron_cap", "steel_helm", "dragon_helm", "aegis_helm"],
    ("knight", "chest"): ["iron_chest", "steel_chest", "dragon_chest", "aegis_chest"],
    ("knight", "feet"): ["iron_boots", "steel_boots", "dragon_boots", "aegis_boots"],
    ("knight", "weapon"): ["iron_sword", "steel_sword", "dragon_blade", "aegis_blade"],
    ("knight", "shield"): ["iron_shield", "steel_shield", "dragon_shield", "aegis_shield"],
    ("mage", "head"): ["cloth_hat", "wizard_hat", "void_hat", "star_hat"],
    ("mage", "chest"): ["cloth_robe", "mage_robe", "void_robe", "star_robe"],
    ("mage", "feet"): ["cloth_shoes", "mage_shoes", "void_shoes", "star_shoes"],
    ("mage", "weapon"): ["wood_staff", "crystal_staff", "void_staff", "star_staff"],
}


def grid(cls, slot, rarity):
    rows = [r.ljust(20, ".")[:20] for r in BASE[(cls, slot)]]
    for y, over in OVER.get((cls, slot, rarity), {}).items():
        row = list(rows[y])
        for x, ch in enumerate(over[:20]):
            if ch != ".":
                row[x] = ch
        rows[y] = "".join(row)
    return rows


MADE_ICONS = {"knight": HERE.parent / "knight" / "icons", "mage": HERE.parent / "wizard" / "icons"}   # user's art


def icon(cls, slot, rarity):
    if cls in MADE_ICONS:
        made = MADE_ICONS[cls] / f"{ITEMS[(cls, slot)][RARITIES.index(rarity)]}.png"
        if made.exists():                          # made by sprite-lab/sprites/knight/gen.py (user's art, recoloured)
            c = Canvas(SIZE, SIZE)
            c.img.alpha_composite(Image.open(made).convert("RGBA"))
            return c
    pal = dict(PAL[cls][rarity])
    for role, fallback in {"n": "h", "N": "l", "w": "h", "W": "l", "c": "l", "C": "m"}.items():
        pal.setdefault(role, pal[fallback])
    rows = grid(cls, slot, rarity)
    art = from_rows(rows, pal)
    c = Canvas(SIZE, SIZE)
    c.paste(art, (SIZE - art.width) // 2, (SIZE - art.height) // 2)
    c.outline(OUTLINE)
    return c


def review(path):
    """Rows: class x rarity, columns: the 6 slots, x4, on the game's panel colour."""
    z = 4
    cell = SIZE * z + 8
    img = Image.new("RGB", (len(SLOTS) * cell + 110, 8 * cell + 8), (24, 21, 34))
    d = ImageDraw.Draw(img)
    r = 0
    for cls in ["knight", "mage"]:
        for k, rarity in enumerate(RARITIES):
            d.text((6, r * cell + cell // 2 - 6), f"{cls[:6]} {rarity[:4]}", fill=(220, 220, 220))
            for s, slot in enumerate(CLASS_SLOTS[cls]):
                ic = icon(cls, slot, rarity).img.resize((SIZE * z, SIZE * z), Image.NEAREST)
                img.paste(ic, (110 + s * cell, r * cell + 4), ic)
            r += 1
    img.save(path)


ANIMATIONS = [(ITEMS[(cls, slot)][k], [icon(cls, slot, rarity)], 1, False, {})
              for cls in ["knight", "mage"] for slot in CLASS_SLOTS[cls] for k, rarity in enumerate(RARITIES)]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(12.0, 12.0), preview_scale=4, gif_scale=4)
    review(HERE / "review.png")
    print(f"OK {NAME}")
