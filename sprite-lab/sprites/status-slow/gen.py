#!/usr/bin/env python3
"""Icon trạng thái "status-slow": làm chậm (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-slow
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-slow"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    b="#5aa9ff"; bd="#245f9a"; w="#ffffff"; sand="#d7b36a"
    # hourglass
    c.rect(4,3,11,4,b); c.rect(4,11,11,12,b)
    c.line(4,4,7,7,bd); c.line(11,4,8,7,bd)
    c.line(4,11,7,8,bd); c.line(11,11,8,8,bd)
    c.rect(6,5,9,5,b); c.rect(5,6,10,6,b)
    c.rect(6,10,9,10,b)
    # sand
    p(c,7,6,sand); p(c,8,6,sand); p(c,7,7,sand); p(c,8,7,sand)
    p(c,8,9,sand); p(c,7,10,sand); p(c,8,10,sand); p(c,9,10,sand)

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
