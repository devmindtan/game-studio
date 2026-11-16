#!/usr/bin/env python3
"""Generator cho sprite "iron-sword": kiếm sắt (legacy)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
sys.path.insert(0,str(HERE.parents[1]/"lib"))
from spritekit import Canvas
from sheet import export

NAME="iron-sword"; W,H=24,24; ANCHOR=(5.0,21.0)

BLADE="#b8c7d9"; BLADE_D="#6b7f96"; BLADE_L="#d8e4f0"; EDGE="#f2fbff"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#d9b44a"; POMMEL="#d9b44a"

def col(c, x, yc, lo, hi, colors):
    """Mot cot doc dien lien (tranh hien tuong caro)."""
    for j, dy in enumerate(range(lo, hi + 1)):
        y = yc + dy
        if 0 <= x < W and 0 <= y < H:
            c.pixel(x, y, colors[j])

def draw(c, glint=False):
    bx, by = 9, 17          # chan luoi
    tx = 20                    # cot dinh
    # luoi: moi cot x co tam y = by-(x-bx), dien day dac
    for x in range(bx, tx + 1):
        yc = by - (x - bx)
        if x >= tx - 1:
            col(c, x, yc, 0, 0, [BLADE_L])         # dinh nhon
        elif x == tx - 2:
            col(c, x, yc, 0, 1, [BLADE_L, BLADE])
        else:
            col(c, x, yc, -1, 1, [BLADE_L, BLADE, BLADE_D])
    # guard vuong goc (cheo xuong-phai, slope +1)
    gx, gy = 9, 17
    for x in range(6, 12 + 1):
        yc = gy + (x - gx)
        col(c, x, yc, 0, 1, [GUARD, HILT_D])
    # can: xuong-trai cung truc voi luoi (slope -1)
    for i in range(3):
        x = gx - 1 - i
        yc = gy + 1 + i
        col(c, x, yc, 0, 1, [HILT, HILT_D])
    # chuom
    px, py = 5, 21
    c.rect(px - 1, py - 1, px + 1, py + 1, POMMEL)
    c.pixel(px - 1, py - 1, GUARD)
    if glint:
        c.pixel(bx + 3, by - 3, EDGE); c.pixel(bx + 6, by - 6, EDGE)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(4, 20, 10, 23, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
