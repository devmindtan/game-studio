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

NAME="greatsword-gold"; W,H=32,32; ANCHOR=(12.0,30.0)

BLADE="#e6c35c"; BLADE_D="#a67c1a"; BLADE_L="#f2d98a"; EDGE="#fff6c8"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#8f6a1f"; POMMEL="#8f6a1f"

def blade_draw(c,glint=False):
    # lưỡi thẳng, rộng, chéo lên-phải
    for i in range(20):
        x = 9 + i
        y = 26 - i
        c.pixel(x, y, BLADE_D)        # viền tối
        c.pixel(x, y-1, BLADE)        # thân
        c.pixel(x, y-2, BLADE)        # thân rộng
        c.pixel(x-1, y-2, BLADE_L)    # viền sáng
    # fuller/rãnh giữa
    for i in range(3, 16):
        x = 9 + i
        y = 26 - i
        c.pixel(x, y-1, BLADE_D)
    # tip
    c.pixel(28, 6, BLADE_L); c.pixel(29, 6, EDGE); c.pixel(28, 7, BLADE); c.pixel(28, 5, BLADE_L)
    # guard rộng
    c.line(6, 24, 11, 29, GUARD)
    c.line(6, 25, 11, 30, HILT_D)
    c.pixel(6, 24, GUARD); c.pixel(11, 29, GUARD)
    # grip dài
    c.line(9, 28, 7, 30, HILT); c.pixel(8, 29, HILT_D)
    # pommel
    c.rect(6, 30, 8, 31, POMMEL)
    if glint:
        c.pixel(16, 18, EDGE); c.pixel(19, 15, EDGE); c.pixel(22, 12, EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(8,30,18,31,"#00000033"); blade_draw(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
