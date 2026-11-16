#!/usr/bin/env python3
"""dagger gold (vật phẩm, dagger)."""
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

NAME="dagger-gold"; W,H=20,20; ANCHOR=(3.0,19.0)

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
    # dao gam ngan, luoi la, dau 2px
    blade(c, 6, 15, 14, -1, 1, [L, M, D], [
        (0, 0, 0, [L]),            # dinh nhon 1px
        (1, -1, 0, [L, M]),        # 2px
        (2, -1, 1, [L, M, D]),     # 3px -> than luoi
    ])
    for x in range(4, 9):
        yc = 15 + (x - 6)
        col(c, x, yc, 0, 1, [GUARD, HILT_D])
    c.pixel(4, 13, GUARD); c.pixel(8, 17, GUARD)
    for i in range(2):
        x, yc = 5 - i, 16 + i
        col(c, x, yc, 0, 1, [HILT, HILT_D])
    c.rect(3, 19, 4, 19, POMMEL); c.pixel(3, 19, GUARD)
    if glint:
        c.pixel(10, 9, E); c.pixel(12, 7, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(2, 18, 7, 19, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
