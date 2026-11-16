#!/usr/bin/env python3
"""bow iron (vật phẩm, bow)."""
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

NAME="bow-iron"; W,H=24,32; ANCHOR=(8.0,26.0)

L="#d8e4f0"; M="#b8c7d9"; D="#6b7f96"; E="#f2fbff"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#d9b44a"; POMMEL="#d9b44a"; ORB="#45a8ff"

def draw(c, glint=False):
    # cung recurve gon: vai cong ro rang, day mong
    STRING = "#d0d0d0"
    upper = [(14,7),(11,8),(8,11),(7,14),(8,16)]
    lower = [(8,19),(7,21),(8,24),(11,26),(14,27)]
    for pts in (upper, lower):
        for i in range(len(pts)-1):
            x1,y1 = pts[i]; x2,y2 = pts[i+1]
            c.line(x1,y1,x2,y2,HILT_D,2)
            c.line(x1,y1,x2,y2,HILT,1)
    # dau cung
    c.rect(13,6,14,7,GUARD); c.rect(13,27,14,28,GUARD)
    c.pixel(13,6,E); c.pixel(13,28,E)
    # day cung
    c.line(14,7,14,27,STRING)
    # tay cam quan
    c.rect(7,15,9,20,GUARD)
    c.rect(8,16,9,19,HILT)
    if glint:
        c.pixel(8,11,E); c.pixel(8,24,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(7, 30, 15, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
