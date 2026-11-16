#!/usr/bin/env python3
"""hammer wood (vật phẩm, hammer)."""
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

NAME="hammer-wood"; W,H=32,32; ANCHOR=(16.0,30.0)

L="#d4a86a"; M="#b07c44"; D="#7a4f2a"; E="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"; ORB="#7ad0a0"

def draw(c, glint=False):
    # can thang giua dau
    c.rect(15,11,16,30,HILT); c.line(15,11,15,30,HILT_D); c.line(16,11,16,30,M)
    # dau búa khoi ngang, be vien
    c.rect(8,4,23,11,D)
    c.rect(9,5,22,10,M)
    c.rect(10,5,21,6,L)
    c.rect(8,5,10,10,D)      # mat
    c.rect(21,5,23,10,D)
    c.line(8,4,23,4,E)
    # vong siet can
    c.rect(14,10,17,12,GUARD); c.pixel(14,10,D); c.pixel(17,10,GUARD)
    c.rect(14,29,17,30,GUARD)
    if glint:
        c.pixel(12,5,E); c.pixel(19,5,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(7, 29, 25, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
