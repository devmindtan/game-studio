#!/usr/bin/env python3
"""sword gold (vật phẩm, sword)."""
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

NAME="sword-gold"; W,H=24,24; ANCHOR=(5.0,22.0)

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
    # luoi cheo 45 do, day dac, dau khong teo (2px o cot cuoi)
    blade(c, 9, 17, 20, -1, 1, [L, M, D], [
        (0, 0, 1, [L, M]),          # dinh: 2px
        (1, -1, 1, [L, M, D]),      # cot ke dinh: day 3px
    ])
    # guard vuong goc truc luoi
    for x in range(6, 13):
        yc = 17 + (x - 9)
        col(c, x, yc, 0, 1, [GUARD, HILT_D])
    c.pixel(6, 14, GUARD); c.pixel(12, 20, GUARD)
    # can cung truc luoi
    for i in range(3):
        x, yc = 8 - i, 18 + i
        col(c, x, yc, 0, 1, [HILT, HILT_D])
    c.rect(5, 22, 6, 22, POMMEL); c.pixel(5, 22, GUARD)
    if glint:
        c.pixel(12, 14, E); c.pixel(15, 11, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(3, 20, 9, 23, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
