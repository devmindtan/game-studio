#!/usr/bin/env python3
"""dagger iron (vật phẩm, dagger)."""
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

NAME="dagger-iron"; W,H=20,20; ANCHOR=(10.0,18.0)
L="#d8e4f0"; M="#b8c7d9"; D="#6b7f96"; E="#f2fbff"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#d9b44a"; POMMEL="#d9b44a"

def draw(c, glint=False):
    # Dao gam thang dung, doi xung quanh truc X=10
    for y in range(4, 12):
        c.pixel(9, y, D); c.pixel(10, y, M); c.pixel(11, y, D)
    c.pixel(10, 2, E); c.pixel(10, 3, L)
    c.pixel(9, 4, D); c.pixel(10, 4, L); c.pixel(11, 4, D)
    # guard ngang tam 10
    c.line(6, 12, 14, 12, GUARD)
    c.line(6, 13, 14, 13, HILT_D)
    c.pixel(6, 12, E); c.pixel(14, 12, E)
    # can
    for y in range(14, 18):
        c.pixel(9, y, HILT_D); c.pixel(10, y, HILT); c.pixel(11, y, HILT_D)
    c.line(9, 18, 11, 18, POMMEL)
    c.pixel(10, 19, POMMEL)
    if glint:
        c.pixel(10, 7, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(7,17,14,19, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
