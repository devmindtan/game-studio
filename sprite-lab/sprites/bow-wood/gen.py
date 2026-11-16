#!/usr/bin/env python3
"""Cung wood (vật phẩm, bow)."""
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

NAME="bow-wood"; W,H=24,32; ANCHOR=(12.0,30.0)

MAIN="#b07c44"; DARK="#7a4f2a"; LIGHT="#d4a86a"; EDGE="#e8cfa0"
STRING="#d8d8d8"; TRIM="#6b4410"

def bow(c,glint=False):
    c.line(14,4,10,8,DARK,2); c.line(10,8,9,16,DARK,2); c.line(9,16,10,24,DARK,2); c.line(10,24,14,28,DARK,2)
    c.line(14,4,11,8,MAIN,1); c.line(11,8,10,16,MAIN,1); c.line(10,16,11,24,MAIN,1); c.line(11,24,14,28,MAIN,1)
    c.line(14,4,14,28,STRING,1)
    c.rect(13,14,15,18,TRIM)
    if glint: c.pixel(10,8,EDGE); c.pixel(10,24,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,16,31,"#00000033"); bow(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
