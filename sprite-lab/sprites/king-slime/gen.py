#!/usr/bin/env python3
"""Generator cho "king-slime": boss ải 10 (Bách Ải), Vua Slime. Cùng dáng với slime (dùng lại bản đồ pixel
của slime) nhưng màu đậm, đội vương miện vàng có ngọc đỏ. Game vẽ ở tỉ lệ lớn (monsters.json scale).
Frame 32x32, neo (16, 31) giữa đáy (ground=True).
Animation: move 4 (nảy), windup 3 (lấy đà: bẹt dần, vương miện rung), jump 2 (vươn cao), hurt 2, death 4.
Chạy: gamekit art run king-slime
"""
import importlib.util
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

_spec = importlib.util.spec_from_file_location("slime_gen", HERE.parent / "slime" / "gen.py")
slime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(slime)

NAME = "king-slime"
SIZE = 32
ANCHOR = (16.0, 31.0)
OUTLINE = "#1b1726"
PAL = {"m": "#3fae6e", "d": "#1f6b45", "l": "#9ff0b8", "w": "#ffffff", "e": "#1b1726", "p": "#ffffff", "t": "#1f5a3a"}
CROWN = ["g.g.g.g", "ggrgggg", "GGGGGGG"]
CROWN_PAL = {"g": "#ffd04a", "G": "#b8862a", "r": "#e8364a"}


def shape(name, dx=0, eyes="open", crown_dy=0, crown=True):
    rows = slime.SHAPES[name]
    if eyes == "closed":
        rows = [r.replace("p", "e") for r in rows]
        rows = [r.replace("ee", "..") if i in (4, 3) else r for i, r in enumerate(rows)]
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    x = (SIZE - art.width) // 2 + dx
    y = 29 - (art.height - 1)
    c.paste(art, x, y)
    if crown:
        cr = from_rows(CROWN, CROWN_PAL)
        c.paste(cr, (SIZE - cr.width) // 2 + dx, y - cr.height + 1 + crown_dy)
    return c.outline(OUTLINE)


ANIMATIONS = [
    ("move", [shape("normal"), shape("squash"), shape("stretch"), shape("normal")], 6, True,
     {"durations_ms": [160, 130, 180, 160], "hitbox": {"shape": "rect", "center": [16.0, 31.0], "active": [0, 3]}}),
    ("windup", [shape("squash"), shape("squash", crown_dy=1), shape("flat", crown_dy=0)], 6, False,
     {"durations_ms": [300, 300, 300], "hitbox": {"shape": "rect", "center": [16.0, 31.0], "active": [0, 2]}}),
    ("jump", [shape("stretch"), shape("stretch", crown_dy=-1)], 8, True,
     {"hitbox": {"shape": "rect", "center": [16.0, 31.0], "active": [0, 1]}}),
    ("hurt", [slime.flash(shape("squash", eyes="closed")), shape("normal", eyes="closed")], 12, False,
     {"durations_ms": [80, 120], "hitbox": {"shape": "rect", "center": [16.0, 31.0], "active": [0, 1]}}),
    ("death", [shape("squash", eyes="closed"), shape("flat", crown=False), shape("puddle", crown=False),
               shape("puddle", crown=False)], 6, False,
     {"durations_ms": [160, 200, 300, 500], "hitbox": {"shape": "rect", "center": [16.0, 31.0], "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move")
    print("OK", NAME)
