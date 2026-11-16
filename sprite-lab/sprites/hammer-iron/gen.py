#!/usr/bin/env python3
"""Búa iron (vật phẩm, hammer)."""
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

NAME="hammer-iron"; W,H=32,32; ANCHOR=(14.0,30.0)

MAIN="#b8c7d9"; DARK="#5f7187"; LIGHT="#d8e4f0"; EDGE="#e8f4ff"
HILT="#8a5a2e"; HILT_D="#563418"; TRIM="#d9b44a"

def hammer(c,glint=False):
    c.line(13,29,18,9,HILT,2); c.line(13,29,18,9,HILT_D,1); c.line(14,28,19,10,"#d8e4f0",1)
    c.rect(10,4,26,11,DARK); c.rect(11,5,25,10,MAIN); c.rect(12,6,24,7,LIGHT)
    c.line(10,4,26,4,EDGE); c.line(10,11,26,11,DARK)
    c.rect(17,9,19,11,TRIM); c.pixel(13,30,TRIM)
    if glint: c.pixel(12,5,EDGE); c.pixel(24,5,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(10,29,20,31,"#00000033"); hammer(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
