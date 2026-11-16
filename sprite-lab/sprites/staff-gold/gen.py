#!/usr/bin/env python3
"""Gậy gold (vật phẩm, staff)."""
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

NAME="staff-gold"; W,H=24,32; ANCHOR=(12.0,30.0)

MAIN="#e6c35c"; DARK="#a67c1a"; LIGHT="#f2d98a"; EDGE="#fff3b0"
TRIM="#8f6a1f"

def staff(c,glint=False):
    c.line(12,29,12,4,MAIN,2); c.line(11,29,11,5,DARK,1); c.line(13,29,13,5,LIGHT,1)
    c.rect(10,3,14,5,TRIM); c.rect(11,2,13,3,TRIM)
    c.pixel(12,29,TRIM)
    if glint: c.pixel(13,8,EDGE); c.pixel(13,16,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,15,31,"#00000033"); staff(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
