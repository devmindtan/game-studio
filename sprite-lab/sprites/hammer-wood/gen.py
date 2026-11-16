#!/usr/bin/env python3
"""Búa wood (vật phẩm, hammer)."""
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

NAME="hammer-wood"; W,H=32,32; ANCHOR=(16.0,30.0)

HEAD="#b07c44"; HEAD_D="#7a4f2a"; HEAD_L="#d4a86a"; EDGE="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; BAND="#6b4410"

def hammer(c,glint=False):
    # cán thẳng, nối vào giữa đầu búa
    c.rect(15,11,17,30,HILT)
    c.line(15,11,15,30,HILT_D)
    c.line(17,11,17,30,HEAD_L)
    c.pixel(15,30,HILT_D); c.pixel(16,30,HILT); c.pixel(17,30,HEAD_L)
    # đầu búa (khối ngang, cân đối)
    c.rect(8,4,24,11,HEAD_D)
    c.rect(9,5,23,10,HEAD)
    c.rect(10,5,22,6,HEAD_L)
    c.line(8,4,24,4,EDGE)
    c.line(8,11,24,11,HEAD_D)
    c.line(8,4,8,11,HEAD_D); c.line(24,4,24,11,HEAD_D)
    # vòng siết cán
    c.rect(14,10,18,11,BAND); c.pixel(14,10,BAND); c.pixel(18,10,BAND)
    if glint:
        c.pixel(11,5,EDGE); c.pixel(21,5,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(11,29,21,31,"#00000033"); hammer(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
