#!/usr/bin/env python3
"""Icon trạng thái "status-regen": hồi phục dần (buff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-regen
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-regen"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    g="#4ade80"; gd="#1f7a45"; gl="#c8ffd9"
    # heart
    pts=[(5,5),(4,6),(4,8),(8,12),(12,8),(12,6),(11,5),(9,5),(8,6),(7,5)]
    c.polygon(pts,g)
    c.line(5,5,4,6,gd); c.line(11,5,12,6,gd); c.line(4,8,8,12,gd); c.line(12,8,8,12,gd)
    p(c,6,6,gl); p(c,5,7,gl)
    # plus
    c.rect(10,2,11,6,gl); c.rect(8,3,13,4,gl)

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
