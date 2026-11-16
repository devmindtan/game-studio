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

NAME="greatsword-wood"; W,H=32,32; ANCHOR=(11.0,30.0)

BLADE="#b07c44"; BLADE_D="#7a4f2a"; BLADE_L="#d4a86a"; EDGE="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"

def blade_draw(c,glint=False):
    # lưỡi thẳng, rộng, chéo lên-phải
    for i in range(19):
        x = 10 + i
        y = 25 - i
        c.pixel(x, y, BLADE_D)
        c.pixel(x, y-1, BLADE)
        c.pixel(x, y-2, BLADE)
        c.pixel(x-1, y-2, BLADE_L)
    # fuller
    for i in range(4, 15):
        x = 10 + i
        y = 25 - i
        c.pixel(x, y-1, BLADE_D)
    # tip
    c.pixel(28, 6, BLADE_L); c.pixel(29, 5, EDGE); c.pixel(28, 5, BLADE_L); c.pixel(29, 6, BLADE)
    # guard rộng, nối đế lưỡi
    c.line(7, 25, 13, 25, GUARD)
    c.line(7, 26, 13, 26, HILT_D)
    c.pixel(13, 24, GUARD)
    # grip
    c.line(10, 27, 10, 29, HILT)
    c.line(9, 27, 9, 29, HILT_D)
    # pommel
    c.rect(9, 30, 11, 30, POMMEL)
    if glint:
        c.pixel(16, 18, EDGE); c.pixel(19, 15, EDGE); c.pixel(22, 12, EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(8,29,14,31,"#00000033"); blade_draw(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
