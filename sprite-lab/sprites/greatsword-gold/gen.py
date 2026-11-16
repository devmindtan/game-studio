#!/usr/bin/env python3
"""greatsword gold (vật phẩm, greatsword)."""
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

NAME="greatsword-gold"; W,H=32,32; ANCHOR=(6.0,29.0)

L="#f2d98a"; M="#e6c35c"; D="#a67c1a"; E="#fff6c8"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#8f6a1f"; POMMEL="#8f6a1f"; ORB="#ff7ac0"

def col(c, x, yc, lo, hi, colors):
    for j, dy in enumerate(range(lo, hi + 1)):
        y = yc + dy
        if 0 <= x < W and 0 <= y < H:
            c.pixel(x, y, colors[j])

def blade(c, bx, by, tx, lo, hi, colors, tips):
    for x in range(bx, tx + 1):
        yc = by - (x - bx)
        dist = tx - x
        tlo, thi, tcolors = lo, hi, colors
        for d, lo2, hi2, cols2 in tips:
            if d == dist:
                tlo, thi, tcolors = lo2, hi2, cols2
                break
        col(c, x, yc, tlo, thi, tcolors)

def draw(c, glint=False):
    blade(c, 11, 23, 27, -2, 1, [L, M, M, D], [
        (0, -1, 1, [L, M, M]),      # dinh 3px, khong teo
        (1, -2, 1, [L, M, M, D]),   # cot ke dinh day 4px
    ])
    # guard rong vuong goc
    for x in range(7, 16):
        yc = 23 + (x - 11)
        col(c, x, yc, 0, 1, [GUARD, HILT_D])
    c.pixel(7, 19, GUARD); c.pixel(15, 27, GUARD)
    # can dai
    for i in range(4):
        x, yc = 10 - i, 24 + i
        col(c, x, yc, 0, 1, [HILT, HILT_D])
    c.rect(6, 29, 7, 29, POMMEL); c.pixel(6, 29, GUARD)
    if glint:
        c.pixel(17, 17, E); c.pixel(20, 14, E); c.pixel(23, 11, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(4, 28, 12, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
