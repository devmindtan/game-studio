#!/usr/bin/env python3
"""Rìu gỗ (vật phẩm, base: axe)."""
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

NAME="axe-wood"; W,H=32,32; ANCHOR=(14.0,30.0)
WOOD="#8a5a2e"; WOOD_D="#563418"; WOOD_L="#b07c44"; HEAD="#b07c44"; HEAD_D="#7a4f2a"; EDGE="#d4a86a"

def axe(c,glint=False):
    c.line(13,29,20,8,WOOD,2); c.line(13,29,20,8,WOOD_D,1); c.line(14,28,20,9,WOOD_L,1)
    c.polygon([(18,7),(12,5),(9,9),(11,12),(16,11)],HEAD_D)
    c.polygon([(18,8),(13,6),(10,9),(12,11),(16,10)],HEAD)
    c.line(12,7,10,9,EDGE)
    c.polygon([(20,9),(25,7),(27,11),(24,14),(20,12)],HEAD_D)
    c.polygon([(20,10),(24,8),(26,11),(23,13),(20,11)],HEAD)
    c.line(25,8,26,11,EDGE)
    c.line(17,10,21,9,WOOD_D); c.pixel(13,30,WOOD_D)
    if glint: c.pixel(11,7,EDGE); c.pixel(25,9,EDGE)

def idle(i):
    c=Canvas(W,H); c.ellipse(10,29,20,31,"#00000033"); axe(c,glint=(i in (2,3))); return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIMATIONS,anchor=ANCHOR)
    print("ok")
