#!/usr/bin/env python3
"""Gậy phép wood (vật phẩm, magic staff)."""
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

NAME="magic-staff-wood"; W,H=24,32; ANCHOR=(12.0,30.0)

MAIN="#b07c44"; DARK="#7a4f2a"; LIGHT="#d4a86a"; EDGE="#e8cfa0"
ORB="#45a8ff"; ORB_L="#9fd7ff"; ORB_D="#2a5fb8"; TRIM="#6b4410"

def staff(c,glint=False):
    c.line(12,29,12,8,MAIN,2); c.line(11,29,11,9,DARK,1); c.line(13,29,13,9,LIGHT,1)
    c.line(10,8,14,8,TRIM); c.line(10,7,10,9,TRIM); c.line(14,7,14,9,TRIM)
    c.ellipse(10,2,14,6,ORB_D); c.ellipse(11,3,13,5,ORB); c.pixel(11,3,ORB_L); c.pixel(12,4,EDGE)
    c.pixel(12,29,TRIM)
    if glint: c.pixel(13,4,EDGE); c.pixel(9,4,ORB_L)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,15,31,"#00000033"); staff(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
