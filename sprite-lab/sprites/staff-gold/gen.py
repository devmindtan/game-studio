#!/usr/bin/env python3
"""Gậy võ thuật (bo staff) gold (vật phẩm, staff - dùng cho class võ thuật)."""
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

MAIN="#e0b84c"; DARK="#a67c1a"; LIGHT="#f2d98a"; EDGE="#fff3b0"
GRIP="#6b4410"; GRIP_D="#4a2f18"

def staff(c,glint=False):
    # thân gậy thẳng, cân đối (võ thuật/bo staff)
    c.rect(11,2,13,30,MAIN)
    c.line(11,2,11,30,DARK)
    c.line(13,2,13,30,LIGHT)
    # đầu gậy
    c.pixel(11,2,EDGE); c.pixel(12,2,EDGE); c.pixel(13,2,LIGHT)
    c.pixel(11,30,DARK); c.pixel(12,30,MAIN); c.pixel(13,30,LIGHT)
    # quấn tay giữa
    for y in range(14,19):
        c.pixel(11,y,GRIP_D); c.pixel(12,y,GRIP); c.pixel(13,y,GRIP_D)
    c.pixel(11,14,GRIP_D); c.pixel(13,18,GRIP_D)
    # quấn gần hai đầu
    for y in range(5,7):
        c.pixel(11,y,GRIP_D); c.pixel(12,y,GRIP); c.pixel(13,y,GRIP_D)
    for y in range(25,27):
        c.pixel(11,y,GRIP_D); c.pixel(12,y,GRIP); c.pixel(13,y,GRIP_D)
    if glint:
        c.pixel(13,10,EDGE); c.pixel(13,22,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,15,31,"#00000033"); staff(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
