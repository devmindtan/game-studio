#!/usr/bin/env python3
"""Generator cho sprite "oak-bow" (legacy)."""
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

NAME="oak-bow"; W,H=24,32; ANCHOR=(10.0,30.0)

L="#d4a86a"; M="#b07c44"; D="#7a4f2a"; E="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"; ORB="#7ad0a0"

def draw(c, glint=False):
    # cung recurve: hai canh cong, day doc o ben phai
    pts = [(13,3),(10,5),(8,9),(8,14),(10,16),(8,22),(8,27),(10,30),(13,31)]
    for i in range(len(pts)-1):
        x1,y1 = pts[i]; x2,y2 = pts[i+1]
        c.line(x1,y1,x2,y2,D,3)
        c.line(x1,y1,x2,y2,M,1)
    c.line(13,3,13,31,HILT_D)
    c.rect(9,14,11,18,GUARD)
    c.rect(10,15,11,17,HILT)
    if glint:
        c.pixel(8,10,E); c.pixel(8,26,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(7, 30, 15, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
