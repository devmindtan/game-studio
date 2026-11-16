#!/usr/bin/env python3
"""shield wood (vật phẩm, shield)."""
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

NAME="shield-wood"; W,H=32,32; ANCHOR=(16.0,29.0)

L="#d4a86a"; M="#b07c44"; D="#7a4f2a"; E="#e8cfa0"
HILT="#8a5a2e"; HILT_D="#563418"; GUARD="#6b4410"; POMMEL="#8a5a2e"; ORB="#7ad0a0"

def draw(c, glint=False):
    # khiên hinh khi (top bang, duoi nhon), vien toi, hien thi kim loai
    def hw(y):
        if y <= 8: return 11
        if y <= 20: return 11 - (y - 8) * 3 // 5
        return max(0, 4 - (y - 20))
    for y in range(4, 29):
        w = hw(y)
        if w <= 0: continue
        c.line(16-w, y, 16+w, y, D)
        c.line(16-w+1, y, 16+w-1, y, M if y > 5 else L)
    # vien tren
    c.line(5,4,27,4,E)
    # hien thi: certain cross
    c.line(16,8,16,24,GUARD)
    c.line(9,14,23,14,GUARD)
    c.rect(14,12,18,16,GUARD); c.rect(15,13,17,15,E)
    c.pixel(16,13,POMMEL)
    if glint:
        c.pixel(10,10,E); c.pixel(22,10,E)

def idle(i):
    c = Canvas(W, H)
    c.ellipse(6, 28, 26, 31, "#00000033")
    draw(c, glint=(i in (2, 3)))
    return c

ANIMATIONS=[("idle",[idle(0)],1,False,{"hitbox":{"shape":"rect","center":[ANCHOR[0],ANCHOR[1]],"active":[0,0]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("ok")
