#!/usr/bin/env python3
"""Icon trạng thái "status-silence": câm lặng/khóa phép (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-silence
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-silence"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    pcol="#b06cff"; pd="#5a2a8a"; pl="#e9d5ff"; x="#ff5a5a"
    # speech bubble with magic
    c.rect(3,4,12,10,pcol); c.rect(4,5,11,9,pl)
    c.rect(4,10,6,12,pcol)
    # mute X
    c.line(5,5,10,10,x); c.line(10,5,5,10,x)
    c.line(4,4,12,4,pd); c.line(3,4,3,10,pd); c.line(12,4,12,10,pd)

def icon():
    c=Canvas(S,S)
    draw(c)
    c.outline("#00000055")
    return c

ANIMATIONS=[("idle",[icon()],1,False)]

def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    preview([strip(flat)], HERE/"preview.png", scale=10)
    gif(flat, HERE/"idle.gif", fps=1, scale=10)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")

if __name__=="__main__": main()
