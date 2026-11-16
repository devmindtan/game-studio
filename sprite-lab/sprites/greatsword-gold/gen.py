#!/usr/bin/env python3
"""Đại kiếm gold (vật phẩm, sword/large)."""
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

NAME="greatsword-gold"; W,H=32,32; ANCHOR=(14.0,30.0)

BLADE="#e6c35c"; BLADE_D="#a67c1a"; BLADE_L="#f2d98a"; EDGE="#fff6c8"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#8f6a1f"; POMMEL="#8f6a1f"

def blade_draw(c,glint=False):
    # lưỡi thẳng, rộng, chéo lên-phải (không méo)
    # light edge (left/top side of blade)
    for j,y in enumerate(range(5,25)):
        x = 22 - j
        c.pixel(x,y,BLADE_L)
    # center
    for j,y in enumerate(range(5,26)):
        x = 21 - j
        c.pixel(x,y,BLADE)
        c.pixel(x-1,y,BLADE)
    # dark edge
    for j,y in enumerate(range(6,26)):
        x = 19 - j
        c.pixel(x,y,BLADE_D)
    # fuller (ranh giữa)
    for j,y in enumerate(range(8,23)):
        x = 20 - j
        c.pixel(x,y,BLADE_D)
    # tip
    c.pixel(22,4,EDGE); c.pixel(21,4,BLADE_L); c.pixel(22,5,BLADE_L); c.pixel(21,5,BLADE)
    # guard (ngang, rộng)
    c.line(5,24,14,21,GUARD); c.line(5,25,14,22,HILT_D)
    c.pixel(5,24,GUARD); c.pixel(14,21,GUARD)
    # grip dài
    c.line(10,23,8,30,HILT); c.pixel(10,24,HILT_D); c.pixel(9,26,HILT_D); c.pixel(8,28,HILT_D)
    # pommel
    c.rect(7,29,9,30,POMMEL)
    if glint:
        c.pixel(20,8,EDGE); c.pixel(18,12,EDGE); c.pixel(16,16,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(7,29,16,31,"#00000033"); blade_draw(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
