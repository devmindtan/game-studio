#!/usr/bin/env python3
"""Icon trạng thái "status-speed-up": tăng tốc (buff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-speed-up
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-speed-up"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    y="#ffd84a"; yd="#b88900"; g="#5cff8d"
    # boot/winged speed lines
    c.rect(4,8,10,11,y); c.rect(5,11,9,13,yd); c.rect(8,6,11,8,y)
    c.line(2,6,6,6,g); c.line(1,8,5,8,g); c.line(2,10,4,10,g)
    # arrow forward/up
    c.line(12,12,12,4,g); c.line(11,5,12,4,g); c.line(13,5,12,4,g)

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
