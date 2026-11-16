#!/usr/bin/env python3
"""Kiếm nhỏ wood (vật phẩm, sword/small)."""
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

NAME="sword-wood"; W,H=24,24; ANCHOR=(11.0,22.0)

BLADE="#b07c44"; BLADE_D="#7a4f2a"; BLADE_L="#d4a86a"; EDGE="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"

def sword(c,glint=False):
    # lưỡi kiếm thẳng, chéo lên-phải (đều, không méo)
    # blade: 2 px wide along diagonal
    for i in range(14):
        x = 9 + i
        y = 19 - i
        c.pixel(x, y, BLADE_D)      # viền tối (dưới-phải)
        c.pixel(x, y-1, BLADE)      # thân
        if i >= 1:
            c.pixel(x-1, y-1, BLADE_L)  # viền sáng (trên-trái)
    # tip
    c.pixel(22, 5, BLADE_L); c.pixel(23, 5, EDGE); c.pixel(22, 6, BLADE)
    # guard (vuông góc với lưỡi, gọn)
    c.line(7, 18, 10, 21, GUARD)
    c.pixel(7, 18, GUARD); c.pixel(10, 21, GUARD)
    # grip
    c.line(8, 20, 7, 22, HILT); c.pixel(8, 21, HILT_D)
    # pommel
    c.pixel(6, 22, POMMEL); c.pixel(7, 22, POMMEL)
    if glint:
        c.pixel(14, 13, EDGE); c.pixel(16, 11, EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(7,21,15,23,"#00000033"); sword(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
