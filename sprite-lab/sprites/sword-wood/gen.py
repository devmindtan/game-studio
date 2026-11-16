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

NAME="sword-wood"; W,H=24,24; ANCHOR=(12.0,22.0)

BLADE="#b07c44"; BLADE_D="#7a4f2a"; BLADE_L="#d4a86a"; EDGE="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"

def sword(c,glint=False):
    # lưỡi kiếm thẳng, chéo lên-phải
    # edge line
    for i,(x,y) in enumerate([(16,5),(15,7),(14,9),(13,11),(12,13),(11,15),(10,17),(9,19)]):
        c.pixel(x,y,BLADE_L)
    # main blade
    for i,(x,y) in enumerate([(15,6),(14,8),(13,10),(12,12),(11,14),(10,16),(9,18),(8,20)]):
        c.pixel(x,y,BLADE)
    # dark edge
    for i,(x,y) in enumerate([(14,7),(13,9),(12,11),(11,13),(10,15),(9,17),(8,19)]):
        c.pixel(x,y,BLADE_D)
    # tip
    c.pixel(17,4,EDGE); c.pixel(16,4,BLADE_L); c.pixel(17,5,BLADE)
    # fuller hint
    c.pixel(13,12,BLADE_D); c.pixel(12,14,BLADE_D)
    # guard
    c.line(7,19,11,17,GUARD); c.pixel(7,19,GUARD); c.pixel(11,17,GUARD)
    c.pixel(7,20,HILT_D)
    # grip
    c.line(8,20,7,22,HILT); c.pixel(8,21,HILT_D)
    # pommel
    c.pixel(7,22,POMMEL)
    if glint:
        c.pixel(15,8,EDGE); c.pixel(14,10,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(7,21,14,23,"#00000033"); sword(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
