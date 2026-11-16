#!/usr/bin/env python3
"""Gậy iron (vật phẩm, staff)."""
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

NAME="staff-iron"; W,H=24,32; ANCHOR=(12.0,30.0)

MAIN="#b8c7d9"; DARK="#5f7187"; LIGHT="#d8e4f0"; EDGE="#e8f4ff"
TRIM="#d9b44a"

def staff(c,glint=False):
    c.line(12,29,12,4,MAIN,2); c.line(11,29,11,5,DARK,1); c.line(13,29,13,5,LIGHT,1)
    c.rect(10,3,14,5,TRIM); c.rect(11,2,13,3,TRIM)
    c.pixel(12,29,TRIM)
    if glint: c.pixel(13,8,EDGE); c.pixel(13,16,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,15,31,"#00000033"); staff(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
