#!/usr/bin/env python3
"""Generator cho "chest": rương báu do quái tinh anh rơi (Bách Ải). Gỗ nâu viền vàng, khóa vàng.
Frame 20x20, neo (10, 18) giữa đáy. idle 6 (ánh vàng chạy qua mép nắp), open 5 (nắp bật, sáng bung).
Chạy: gamekit art run chest
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

NAME = "chest"
S = 20
PAL = {"w": "#8a5a2e", "W": "#5a3a1e", "l": "#b07a44", "g": "#ffd04a", "G": "#b8862a", "k": "#3a2410", "y": "#fff2a8"}
LID = [
    "..gggggggggggg..",
    ".gllllllllllllg.",
    ".glwwwwwwwwwwlg.",
    ".gwwwwwwwwwwwwg.",
    ".GGGGGGggGGGGGG.",
]
BOX = [
    ".gwwwwwgyywwwwg.",
    ".gwwwwwgGGwwwwg.",
    ".gwwwwwwwwwwwwg.",
    ".gWWWWWWWWWWWWg.",
    ".gWWWWWWWWWWWWg.",
    ".GGGGGGGGGGGGGG.",
]
OPEN_LID = [
    "..gggggggggggg..",
    ".GkkkkkkkkkkkkG.",
]


def frame(lid_up=0, glint=-1, open_=False, light=0):
    c = Canvas(S, S)
    box = from_rows(BOX, PAL)
    c.paste(box, 2, 18 - box.height + 1)
    if open_:
        lid = from_rows(OPEN_LID, PAL)
        c.paste(lid, 2, 18 - box.height - lid.height + 1 - lid_up)
        for k in range(light):           # light rising from the open chest
            for x in range(5 + k, 15 - k):
                c.pixel(x, 18 - box.height - 1 - k * 2, "#fff2a8")
    else:
        lid = from_rows(LID, PAL)
        c.paste(lid, 2, 18 - box.height - lid.height + 1)
        if glint >= 0:
            c.pixel(3 + glint, 18 - box.height - lid.height + 1, "#ffffff")
    return c.outline("#1b1726")


ANIMATIONS = [
    ("idle", [frame(glint=g) for g in (-1, 2, 5, 8, 11, -1)], 8, True, {}),
    ("open", [frame(open_=True, lid_up=1), frame(open_=True, lid_up=2, light=1), frame(open_=True, lid_up=3, light=2),
              frame(open_=True, lid_up=3, light=3), frame(open_=True, lid_up=3, light=2)], 10, False, {}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=(10.0, 18.0))
    print("OK", NAME)
