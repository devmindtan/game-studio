#!/usr/bin/env python3
"""Đại kiếm gold (vật phẩm, sword/large)."""
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

NAME="greatsword-gold"; W,H=32,32; ANCHOR=(6.0,28.0)

BLADE="#e6c35c"; BLADE_D="#a67c1a"; BLADE_L="#f2d98a"; EDGE="#fff6c8"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#8f6a1f"; POMMEL="#8f6a1f"

def col(c, x, yc, lo, hi, colors):
    """Mot cot doc dien lien (tranh hien tuong caro)."""
    for j, dy in enumerate(range(lo, hi + 1)):
        y = yc + dy
        if 0 <= x < W and 0 <= y < H:
            c.pixel(x, y, colors[j])

def draw(c, glint=False):
    bx, by = 11, 23          # chan luoi
    tx = 27                    # cot dinh
    # luoi: moi cot x co tam y = by-(x-bx), dien day dac
    for x in range(bx, tx + 1):
        yc = by - (x - bx)
        if x >= tx - 1:
            col(c, x, yc, 0, 0, [BLADE_L])         # dinh nhon
        elif x == tx - 2:
            col(c, x, yc, 0, 1, [BLADE_L, BLADE])
        else:
            col(c, x, yc, -2, 1, [BLADE_L, BLADE, BLADE, BLADE_D])
    # guard vuong goc (cheo xuong-phai, slope +1)
    gx, gy = 11, 23
    for x in range(7, 15 + 1):
        yc = gy + (x - gx)
        col(c, x, yc, 0, 1, [GUARD, HILT_D])
    # can: xuong-trai cung truc voi luoi (slope -1)
    for i in range(4):
        x = gx - 1 - i
        yc = gy + 1 + i
        col(c, x, yc, 0, 1, [HILT, HILT_D])
    # chuom
    px, py = 6, 28
    c.rect(px - 1, py - 1, px + 1, py + 1, POMMEL)
    c.pixel(px - 1, py - 1, GUARD)
    if glint:
        c.pixel(bx + 3, by - 3, EDGE); c.pixel(bx + 6, by - 6, EDGE)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(5, 27, 13, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
