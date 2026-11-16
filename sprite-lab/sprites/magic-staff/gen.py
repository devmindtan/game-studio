#!/usr/bin/env python3
"""Generator cho sprite "magic-staff" (legacy)."""
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

NAME="magic-staff"; W,H=24,32; ANCHOR=(12.0,30.0)

L="#d4a86a"; M="#b07c44"; D="#7a4f2a"; E="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"; ORB="#7ad0a0"

def draw(c, glint=False):
    # tham thang, gia do ngoc lon hon, vong trang tri
    c.rect(11,9,12,30,M); c.line(11,9,11,30,D); c.line(12,9,12,30,L)
    for y in (19,25):
        c.line(10,y,13,y,GUARD); c.pixel(10,y,D); c.pixel(13,y,GUARD)
    # gia giu ngoc
    c.line(11,9,9,7,GUARD); c.line(12,9,14,7,GUARD)
    c.line(9,7,11,5,HILT_D); c.line(14,7,12,5,HILT_D)
    c.rect(9,7,14,8,GUARD)
    # ngoc 4x4 + loi sang
    c.ellipse(9,1,14,7,D)
    c.ellipse(10,2,13,6,ORB)
    c.ellipse(11,2,12,4,E)
    c.pixel(10,3,L); c.pixel(13,3,L)
    if glint:
        c.pixel(12,2,E); c.pixel(11,10,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 29, 15, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
