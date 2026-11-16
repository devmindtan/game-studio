#!/usr/bin/env python3
"""Icon trạng thái "status-atk-up": tăng sát thương (buff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-atk-up
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-atk-up"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    red="#ff5a5a"; rd="#9a2020"; y="#ffd84a"; g="#5cff8d"
    # sword
    c.line(8,2,8,11,red); c.line(7,3,7,10,rd); c.line(9,3,9,10,red)
    c.rect(5,10,11,11,y); c.rect(7,12,9,14,rd)
    # up arrow
    c.line(12,9,12,3,g); c.line(11,4,12,3,g); c.line(13,4,12,3,g)

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
