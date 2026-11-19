#!/usr/bin/env python3
"""Generator cho "chest-gold": Rương vàng hiếm (Bách Ải, design/events.md). Cùng dáng và tỷ lệ với "chest"
(nâng cấp từ rương thường, không vẽ lại): thân vàng, đai trắng, khóa ngọc đỏ, sao lấp lánh quanh nắp.
Frame 20x20, neo (10, 18) giữa đáy. idle 6 (ánh trắng chạy qua nắp + sao nháy), open 5 (nắp bật, sáng bung).
Chạy: gamekit art run chest-gold
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from spritekit import Canvas, from_rows
from sheet import export

NAME = "chest-gold"
S = 20
PAL = {"w": "#f0b830", "W": "#b8781a", "l": "#ffe27a", "g": "#fff6d0", "G": "#c89a40", "k": "#5a3008", "y": "#ff3a4a", "r": "#a01828"}
LID = [
    "..gggggggggggg..",
    ".gllllllllllllg.",
    ".glwwwwwwwwwwlg.",
    ".gwwwwwwwwwwwwg.",
    ".GGGGGGggGGGGGG.",
]
BOX = [
    ".gwwwwwgyygwwwg.",
    ".gwwwwwgrrgwwwg.",
    ".gwwwwwwwwwwwwg.",
    ".gWWWWWWWWWWWWg.",
    ".gWWWWWWWWWWWWg.",
    ".GGGGGGGGGGGGGG.",
]
OPEN_LID = [
    "..gggggggggggg..",
    ".GkkkkkkkkkkkkG.",
]


STARS = [(2, 4), (17, 3), (13, 1), (6, 2)]   # sparkles above the lid, clear of the outline (x, y)


def frame(lid_up=0, glint=-1, open_=False, light=0, star=-1):
    c = Canvas(S, S)
    box = from_rows(BOX, PAL)
    c.paste(box, 2, 18 - box.height + 1)
    if open_:
        lid = from_rows(OPEN_LID, PAL)
        c.paste(lid, 2, 18 - box.height - lid.height + 1 - lid_up)
        for k in range(light):           # light rising from the open chest
            for x in range(5 + k, 15 - k):
                c.pixel(x, 18 - box.height - 1 - k * 2, "#ffffff" if k % 2 == 0 else "#fff2a8")
    else:
        lid = from_rows(LID, PAL)
        c.paste(lid, 2, 18 - box.height - lid.height + 1)
        if glint >= 0:
            c.pixel(3 + glint, 18 - box.height - lid.height + 1, "#ffffff")
    c = c.outline("#1b1726")
    if 0 <= star < len(STARS):   # a 4-point twinkle, after the outline so it stays white
        x, y = STARS[star]
        c.pixel(x, y, "#ffffff")
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c.pixel(x + dx, y + dy, "#fff2a8")
    return c


ANIMATIONS = [
    ("idle", [frame(glint=g, star=st) for g, st in ((-1, 0), (2, -1), (5, 1), (8, 2), (11, -1), (-1, 3))], 8, True, {}),
    ("open", [frame(open_=True, lid_up=1), frame(open_=True, lid_up=2, light=1), frame(open_=True, lid_up=3, light=2),
              frame(open_=True, lid_up=3, light=3), frame(open_=True, lid_up=3, light=2)], 10, False, {}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(10.0, 18.0))
    print("OK", NAME)
