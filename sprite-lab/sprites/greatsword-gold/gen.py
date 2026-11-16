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

NAME="greatsword-gold"; W,H=32,32; ANCHOR=(16.0,30.0)
L="#f2d98a"; M="#e6c35c"; D="#a67c1a"; E="#fff6c8"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#8f6a1f"; POMMEL="#8f6a1f"

def draw(c, glint=False):
    # Dai kiem thang dung, doi xung quanh truc X=16
    for y in range(5, 22):
        c.pixel(14, y, D); c.pixel(15, y, M)
        c.pixel(16, y, L)
        c.pixel(17, y, M); c.pixel(18, y, D)
    # dinh nhon
    c.pixel(16, 3, E); c.pixel(15, 4, L); c.pixel(16, 4, M); c.pixel(17, 4, L)
    # guard ngang tam 16
    c.line(9, 22, 23, 22, GUARD)
    c.line(9, 23, 23, 23, HILT_D)
    c.pixel(9, 22, E); c.pixel(23, 22, E)
    # can 3px cung truc
    for y in range(24, 30):
        c.pixel(15, y, HILT_D); c.pixel(16, y, HILT); c.pixel(17, y, HILT_D)
    # pommel
    c.line(14, 30, 18, 30, POMMEL)
    c.pixel(16, 31, POMMEL)
    if glint:
        c.pixel(16, 8, E); c.pixel(16, 15, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(11,29,21,31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
