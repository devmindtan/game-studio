#!/usr/bin/env python3
"""Icon trạng thái "status-def-up": tăng phòng thủ (buff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-def-up
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-def-up"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    s="#7fa6c9"; sd="#3f5f7a"; sl="#d7ecff"; g="#5cff8d"
    # shield
    c.polygon([(4,3),(11,3),(11,9),(7,13),(4,9)],s)
    c.line(4,3,4,9,sd); c.line(11,3,11,9,sd); c.line(4,9,7,13,sd); c.line(11,9,7,13,sd)
    c.line(7,4,7,12,sl); c.line(5,7,10,7,sl)
    # up arrow
    c.line(13,10,13,4,g); c.line(12,5,13,4,g); c.line(14,5,13,4,g)

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
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp,"hitbox":{"shape":"rect","center":[float(ANCHOR[0]),float(ANCHOR[1])],"active":[0,len(f)-1]}} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")

if __name__=="__main__": main()
