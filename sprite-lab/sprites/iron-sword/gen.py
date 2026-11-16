#!/usr/bin/env python3
"""Generator cho sprite "iron-sword" (legacy)."""
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

NAME="iron-sword"; W,H=24,24; ANCHOR=(12.0,22.0)
L="#d8e4f0"; M="#b8c7d9"; D="#6b7f96"; E="#f2fbff"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#d9b44a"; POMMEL="#d9b44a"

def draw(c, glint=False):
    # Luoi thang dung, doi xung quanh truc X=12
    for y in range(6, 16):
        c.pixel(11, y, D); c.pixel(12, y, M); c.pixel(13, y, D)
    # dinh nhon doi xung
    c.pixel(12, 4, L); c.pixel(12, 5, L)
    c.pixel(11, 6, D); c.pixel(12, 6, L); c.pixel(13, 6, D)
    # guard ngang, tam dung 12
    c.line(7, 16, 17, 16, GUARD)
    c.line(7, 17, 17, 17, HILT_D)
    c.pixel(7, 16, E); c.pixel(17, 16, E)
    # can 3px, cung truc
    for y in range(18, 22):
        c.pixel(11, y, HILT_D); c.pixel(12, y, HILT); c.pixel(13, y, HILT_D)
    # pommel 3px, cung truc
    c.line(11, 22, 13, 22, POMMEL)
    c.pixel(12, 23, POMMEL)
    if glint:
        c.pixel(12, 9, E); c.pixel(12, 13, E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(8,21,15,23, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
