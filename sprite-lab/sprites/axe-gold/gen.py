#!/usr/bin/env python3
"""Rìu vàng (vật phẩm, base: axe)."""
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

NAME="axe-gold"; W,H=32,32; ANCHOR=(14.0,30.0)
WOOD="#8a5a2e"; WOOD_D="#563418"; WOOD_L="#b07c44"; GOLD="#e6c35c"; GOLD_D="#a67c1a"; EDGE="#fff3b0"; TRIM="#8f6a1f"

def axe(c,glint=False):
    c.line(13,29,20,7,WOOD,2); c.line(13,29,20,7,WOOD_D,1); c.line(14,28,20,8,WOOD_L,1)
    c.polygon([(18,6),(12,4),(8,8),(10,12),(16,11)],GOLD_D)
    c.polygon([(18,7),(13,5),(10,8),(11,11),(16,10)],GOLD)
    c.line(12,6,10,8,EDGE)
    c.polygon([(20,8),(26,6),(28,10),(25,14),(20,12)],GOLD_D)
    c.polygon([(20,9),(25,7),(27,10),(24,13),(20,11)],GOLD)
    c.line(26,7,27,10,EDGE)
    c.line(17,9,21,8,TRIM); c.line(17,10,21,9,TRIM); c.pixel(13,30,GOLD)
    if glint: c.pixel(11,6,EDGE); c.pixel(26,8,EDGE); c.pixel(19,8,"#ffffff")

def idle(i):
    c=Canvas(W,H); c.ellipse(10,29,20,31,"#00000033"); axe(c,glint=(i in (2,3))); return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIMATIONS,anchor=ANCHOR)
    print("ok")
