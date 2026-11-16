#!/usr/bin/env python3
"""Khiên iron (vật phẩm, shield)."""
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

NAME="shield-iron"; W,H=32,32; ANCHOR=(16.0,30.0)

MAIN="#b8c7d9"; DARK="#5f7187"; LIGHT="#d8e4f0"; EDGE="#e8f4ff"
TRIM="#d9b44a"; RIM="#3a2a1a"

def shield(c,glint=False):
    c.polygon([(16,5),(26,9),(26,20),(16,27),(6,20),(6,9)],DARK)
    c.polygon([(16,6),(25,10),(25,20),(16,26),(7,20),(7,10)],MAIN)
    c.polygon([(16,8),(23,11),(23,19),(16,24),(9,19),(9,11)],LIGHT)
    c.line(16,6,16,26,TRIM); c.line(7,14,25,14,TRIM)
    c.rect(14,12,18,16,TRIM); c.pixel(16,14,EDGE)
    c.line(16,5,26,9,EDGE); c.line(6,9,16,5,EDGE)
    if glint: c.pixel(10,11,EDGE); c.pixel(22,11,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(10,28,22,31,"#00000033"); shield(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
