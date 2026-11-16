#!/usr/bin/env python3
"""Icon trạng thái "status-burn": bỏng/lửa (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-burn
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-burn"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    red="#ff6a00"; org="#ff9f1a"; yel="#ffe066"; dark="#a03000"
    # flame
    for x,y in [(8,2),(7,3),(8,3),(9,3),(6,4),(7,4),(8,4),(9,4),(10,4),
                (5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),
                (5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),
                (5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),
                (6,8),(7,8),(8,8),(9,8),(10,8),(6,9),(7,9),(8,9),(9,9),(10,9),
                (7,10),(8,10),(9,10),(7,11),(8,11),(9,11),(8,12)]:
        p(c,x,y,red)
    for x,y in [(8,4),(7,5),(8,5),(9,5),(7,6),(8,6),(9,6),(7,7),(8,7),(9,7),(8,8),(8,9)]:
        p(c,x,y,org)
    for x,y in [(8,6),(8,7),(8,8)]:
        p(c,x,y,yel)
    for x,y in [(5,8),(11,8),(6,10),(10,10)]:
        p(c,x,y,dark)

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
