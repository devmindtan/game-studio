#!/usr/bin/env python3
"""staff iron (vật phẩm, staff)."""
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

NAME="staff-iron"; W,H=24,32; ANCHOR=(12.0,30.0)

L="#d8e4f0"; M="#b8c7d9"; D="#6b7f96"; E="#f2fbff"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#d9b44a"; POMMEL="#d9b44a"; ORB="#45a8ff"

def draw(c, glint=False):
    # bo staff: than thang, dau loe nhẹ, quan tay 3 doan
    c.rect(11,2,12,30,M); c.line(11,2,11,30,D); c.line(12,2,12,30,L)
    c.rect(10,2,13,3,E); c.rect(10,29,13,30,D)
    for a,b in [(6,8),(14,17),(24,26)]:
        for y in range(a,b+1):
            c.pixel(11,y,HILT_D); c.pixel(12,y,HILT)
    if glint:
        c.pixel(12,11,E); c.pixel(12,20,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 29, 15, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
