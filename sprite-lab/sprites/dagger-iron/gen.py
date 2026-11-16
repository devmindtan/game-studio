#!/usr/bin/env python3
"""Dao găm iron (vật phẩm, dagger)."""
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

NAME="dagger-iron"; W,H=20,20; ANCHOR=(10.0,18.0)

MAIN="#b8c7d9"; DARK="#5f7187"; LIGHT="#d8e4f0"; EDGE="#e8f4ff"
HILT="#8a5a2e"; HILT_D="#563418"; TRIM="#d9b44a"

def dagger(c,glint=False):
    c.line(10,17,14,6,DARK,2); c.line(9,17,13,6,MAIN,1); c.line(9,16,13,7,LIGHT,1)
    c.pixel(14,5,EDGE); c.pixel(14,6,MAIN)
    c.line(7,16,12,15,TRIM); c.line(7,17,12,16,HILT_D)
    c.line(9,17,8,18,HILT,2); c.pixel(8,18,TRIM)
    if glint: c.pixel(13,7,EDGE); c.pixel(12,9,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(7,17,13,19,"#00000033"); dagger(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
