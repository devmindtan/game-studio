#!/usr/bin/env python3
"""Đại kiếm wood (vật phẩm, sword/large)."""
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

NAME="greatsword-wood"; W,H=32,32; ANCHOR=(16.0,30.0)

MAIN="#b07c44"; DARK="#7a4f2a"; LIGHT="#d4a86a"; EDGE="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; TRIM="#6b4410"

def blade(c,glint=False):
    c.polygon([(14,28),(10,27),(22,4),(25,5)],DARK)
    c.polygon([(14,27),(11,26),(22,5),(24,6)],MAIN)
    c.line(12,26,22,6,LIGHT); c.line(13,26,23,6,MAIN)
    c.line(13,25,22,7,DARK)
    c.pixel(23,4,EDGE); c.pixel(24,4,MAIN); c.pixel(23,5,MAIN)
    c.line(8,25,18,22,TRIM); c.line(8,26,18,23,HILT_D)
    c.pixel(8,25,TRIM); c.pixel(18,22,TRIM)
    c.line(13,26,11,30,HILT,2); c.line(13,26,11,30,HILT_D,1)
    c.pixel(11,30,TRIM); c.rect(10,29,12,30,TRIM)
    if glint:
        for i in range(4):
            y=20-i*3
            if 6<=y<=25:
                x=12+(26-y)*10//20
                c.pixel(x,y,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,20,31,"#00000033"); blade(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
