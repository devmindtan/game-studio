#!/usr/bin/env python3
"""Gậy phép iron (vật phẩm, magic staff)."""
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

NAME="magic-staff-iron"; W,H=24,32; ANCHOR=(12.0,30.0)

MAIN="#a8b4c4"; DARK="#5f7187"; LIGHT="#d0dce8"; EDGE="#e8f4ff"
TRIM="#d9b44a"; TRIM_D="#8f6a1f"
ORB="#45a8ff"; ORB_L="#9fd7ff"; ORB_D="#2a5fb8"; CORE="#ffffff"

def staff(c,glint=False):
    # thân gậy thẳng
    c.rect(11,9,13,30,MAIN)
    c.line(11,9,11,30,DARK)
    c.line(13,9,13,30,LIGHT)
    c.pixel(11,30,DARK); c.pixel(12,30,MAIN); c.pixel(13,30,LIGHT)
    # vòng trang trí
    c.line(10,20,14,20,TRIM); c.pixel(10,20,TRIM_D); c.pixel(14,20,TRIM_D)
    c.line(10,26,14,26,TRIM)
    # giá giữ ngọc
    c.line(11,9,10,7,TRIM); c.line(13,9,14,7,TRIM)
    c.line(10,7,11,6,TRIM_D); c.line(14,7,13,6,TRIM_D)
    c.rect(10,8,14,9,TRIM)
    # ngọc phép
    c.ellipse(10,2,14,6,ORB_D)
    c.ellipse(11,3,13,5,ORB)
    c.pixel(11,3,ORB_L); c.pixel(12,4,CORE)
    if glint:
        c.pixel(13,3,EDGE); c.pixel(9,4,ORB_L); c.pixel(13,14,EDGE)

def idle(i): c=Canvas(W,H); c.ellipse(9,29,15,31,"#00000033"); staff(c,glint=(i in (2,3))); return c
ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__": export(HERE,NAME,ANIMATIONS,anchor=ANCHOR); print("ok")
