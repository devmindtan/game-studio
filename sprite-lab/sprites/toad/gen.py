#!/usr/bin/env python3
"""Generator cho "toad" (Cóc Độc): quái nhảy của Đầm Lầy Độc (Bách Ải 6A).

Mô tả đầy đủ + tham khảo: games/bach-ai/design/art/toads.md. Vẽ tay từng tư thế (ASCII; khung 32x24 quá nhỏ để vẽ bằng hình học):
đùi sau gập, tay trước chống, mắt có gờ mày và đồng tử ngang, tuyến độc sau mắt, miệng rộng, mụn độc nổi
khối dọc sống lưng. Frame 32x24, quay phải, neo (16, 23).
move 4 (ngồi, họng phập phồng), crouch 2 (lấy đà), jump 4 (bật → đỉnh → rơi → đáp; game nâng sprite theo
đường cong), hurt 2, death 4 (bẹp, chảy thành vũng độc). Chạy: gamekit art run toad
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

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402
from spritekit import from_rows  # noqa: E402

NAME = "toad"
W, H = 32, 24
ANCHOR = (16.0, 23.0)
OUTLINE = "#14160c"
POOL, POOL_L = "#4a8a22", "#8ad040"
# hand-drawn poses (games/bach-ai/design/art/toads.md): K side shade, g back, l/L lit, b belly, t throat,
# d belly shade, o/O/r poison wart (mid/light/dark), e eye, p pupil (horizontal), w glint, n brow/mouth, G gland
PAL = {"K": "#38401c", "g": "#5e6a2a", "l": "#8a8a3a", "L": "#a8a850", "b": "#d8c47a", "t": "#efe2a8",
       "d": "#b09a58", "o": "#e0702a", "O": "#ffb04a", "r": "#8a3a1a", "e": "#f0c040", "p": "#14160c",
       "w": "#fff6c8", "n": "#2a2a14", "G": "#a0a048"}
SIT = [
    ".................nnn......",
    "................neeen.....",
    "...............nepwpen....",
    "..........LLLLLneeeeen....",
    "........LLlGGGlnnnnngl....",
    "......LLlOlGGGGlllllllgl..",
    ".....LlgOrlgggglLlllllggl.",
    "....LlgrrggOggggggggggggg.",
    "...lgggggglOrggnnnnnnnnnnn",
    "..lgggOlgggrrgggggtttttbbK",
    "..gglOrgggggggggbbttttbbK.",
    ".KgggrrgggKKKggbbbbbbbbK..",
    ".KglllgggKlllKgbbbbbbbKgK.",
    "KgllLLlgKllLLlKdbbbbbKglK.",
    "KgglllggKlllllKKdddKKgglK.",
    ".KKgggKKgKKKKggKKKKKKgglK.",
    "..KKKKgggKKgggggK....KgglK",
    "......KKKKKKKKKKK...KlKlKlK",
]
PUFF = list(SIT)
PUFF[9] = "..lgggOlgggrrggggtttttttbbK"
PUFF[10] = "..gglOrgggggggggbtttttttbK."
PUFF[11] = ".KgggrrgggKKKggbbttttttbK.."
CROUCH = [
    ".................nnn.......",
    "................neeen......",
    "...............nepwpen.....",
    "........LLLLLLLneeeeen.....",
    "......LLlOlGGGGlnnnnngl....",
    "....LlgOrlggggglLlllllggl..",
    "...lgggrrggOggggggggggggggK",
    "..lggOlgggglOrgnnnnnnnnnnnK",
    ".KglOrgggggrrgggggtttttbbK.",
    "KgllLLlgKKKggbbbbbbbbbbbKgK",
    "KgglLLlKlllLKdbbbbbbbbKggglK",
    ".KKgllKKlLLllKKKKKKKKKgglgK",
    "..KKKKKKKKKKKKK.....KlKlKlK",
]
TAKEOFF = [
    "......................nnn..",
    ".....................neeen.",
    "....................nepwpen",
    "...............LLLLneeeen..",
    ".............LLlGGlnnnngl..",
    "...........LlOlGGGlllllgK..",
    ".........LlgOrgggglllllgK..",
    ".......LlggrrgOggggnnnnnK..",
    ".....LlgggggglOrgtttbbbK...",
    "....lggOlggggrrgbtttbbK....",
    "...lglOrggggggbbbbbbbKglK..",
    "..KggrrgggKKKbbbbbbbK.KglK.",
    ".KgllLLlgKlLKdbbbbKK...KlK.",
    ".KglLLlKKlLlKKKKKK.........",
    "KgllKKKKlLlK...............",
    "KllK...KllK................",
    "KlK....KlK.................",
    "KKKK...KKKK................",
]
APEX = [
    ".....................nnn........",
    "....................neeen.......",
    "...................nepwpen......",
    "...........LLLLLLLLneeeen.......",
    ".........LLlOlGGGGlnnnngl.......",
    ".......LlgOrlggggglllllllggl....",
    ".....LlggrrggOgggggggggggggggK..",
    "KK.LlgggggglOrggnnnnnnnnnnnnnK..",
    "KlKlgggOlgggrrggggggtttttbbbbK..",
    "KllgglOrgggggggbbbbbbbbbbbbbKKKK",
    ".KlllgrrgggKKKbbbbbbbbbbbbKggllK",
    "..KKllLLlgKllKKKKKKKKKKKKKKKKKKK",
    "....KKKKKKKKKK..................",
]
FALL = [
    ".................nnn......",
    "................neeen.....",
    "...............nepwpen....",
    "..........LLLLLneeeeen....",
    "........LLlGGGlnnnnngl....",
    "......LLlOlGGGGlllllllgl..",
    ".....LlgOrlgggglLlllllggl.",
    "....LlgrrggOggggggggggggg.",
    "...lgggggglOrggnnnnnnnnnnn",
    "..lgggOlgggrrgggggtttttbbK",
    ".KgglOrgggggggggbbttttbbK.",
    ".KgllLLlgKKKggbbbbbbbbKgK.",
    "..KgllLLKlllKbbbbbbbbKgglK",
    "...KKgllKlLlKKddddKKK.KglK",
    ".....KKKKKlLlK.......KglK.",
    ".........KKKK.......KlKlK.",
]
LAND = CROUCH[:6] + [
    "...lgggrrggOggggggggggggggggK",
    "..lggOlgggglOrgnnnnnnnnnnnnnK",
    ".KglOrgggggrrgggggtttttbbbbK.",
    "KgllLLlgKKKggbbbbbbbbbbbbbKgK",
    "KgglLLlKlllLKdbbbbbbbbbbKggglK",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKlKlK",
]
FLAT = [
    "..............nnn.........",
    ".............nnnnn........",
    "......LLLLLLLnnnnnn.......",
    "...LLlOlGGGGlllllllgl.....",
    ".LlgOrlgggggggnnnnnnnnK...",
    "KgggrrgggOggggggttttbbbK..",
    "KgllLLlgKKKbbbbbbbbbbbbbKK",
    "KKKKKKKKKKKKKKKKKKKKKKKKKK",
]


def frame(rows, dx=0):
    w = max(len(r) for r in rows)
    art = from_rows([r.ljust(w, ".") for r in rows], PAL)
    c = Canvas(W, H)
    c.paste(art, (W - art.width) // 2 + dx, 21 - (art.height - 1))   # every pose on the floor: the game lifts it
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x14, 0x16, 0x0c):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def puddle(k):
    c = Canvas(W, H)
    w = [11, 13, 14][k]
    c.ellipse(16 - w, 19, 16 + w, 21, POOL, fill=True)
    c.ellipse(16 - w + 4, 19, 16 + w - 6, 20, POOL_L, fill=True)
    if k < 2:
        c.rect(12, 19 - (1 - k), 19, 20, PAL["g"], fill=True)   # what is left of the toad
        c.pixel(14, 19 - (1 - k), PAL["o"])
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [16.0, 23.0]}
ANIMATIONS = [
    ("move", [frame(SIT), frame(PUFF), frame(SIT, 1), frame(PUFF, 1)], 8, True,
     {"durations_ms": [240, 180, 240, 180], "hitbox": {**HB, "active": [0, 3]}}),
    ("crouch", [frame(CROUCH), frame(LAND)], 8, False,
     {"durations_ms": [180, 300], "hitbox": {**HB, "active": [0, 1]}}),
    ("jump", [frame(TAKEOFF), frame(APEX), frame(FALL), frame(LAND)], 8, False,
     {"durations_ms": [110, 170, 130, 110], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [frame(CROUCH), frame(APEX), frame(LAND)], 8, False,
     {"durations_ms": [200, 160, 160], "hitbox": {**HB, "active": [1, 2]}}),
    ("hurt", [flash(frame(SIT)), frame(SIT, -1)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(frame(FLAT), 0.4), puddle(0), puddle(1), puddle(2)], 8, False,
     {"durations_ms": [120, 160, 180, 240], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
