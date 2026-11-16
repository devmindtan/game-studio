#!/usr/bin/env python3
"""Kiếm nhỏ iron (vật phẩm, sword/small)."""
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

NAME="sword-iron"; W,H=24,24; ANCHOR=(12.0,22.0)

MAIN="#b8c7d9"; DARK="#5f7187"; LIGHT="#d8e4f0"; EDGE="#e8f4ff"
HILT="#8a5a2e"; HILT_D="#563418"; TRIM="#d9b44a"

def sword(c,glint=False):
    c.line(11,21,17,6,DARK,2); c.line(10,21,16,6,MAIN,1); c.line(10,20,15,7,LIGHT,1)
    c.pixel(17,5,EDGE); c.pixel(17,6,MAIN); c.pixel(16,5,MAIN)
    c.line(8,19,13,17,TRIM); c.line(8,20,13,18,HILT_D)
    c.line(10,20,9,22,HILT,2); c.line(10,20,9,22,HILT_D,1); c.pixel(9,22,TRIM)
    if glint:
        for dy in (0,1,2):
            y=16-dy*2
            if 6<=y<=20: c.pixel(11+(20-y)//3,y,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(8,21,15,23,"#00000033"); sword(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
