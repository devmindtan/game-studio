#!/usr/bin/env python3
"""Icon trạng thái "status-poison": trúng độc (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-poison
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-poison"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    g="#4caf50"; gd="#1f6b2a"; gl="#a8ff6a"; bub="#c8ff9a"
    # skull-like poison drop
    c.ellipse(4,5,11,12,g); c.ellipse(5,6,10,11,gl)
    # eyes
    c.rect(6,7,7,8,gd); c.rect(9,7,10,8,gd)
    # mouth drops
    c.rect(7,10,9,10,gd); p(c,7,11,gd); p(c,9,11,gd)
    # bubbles
    c.ellipse(10,2,12,4,bub); c.ellipse(2,3,4,5,bub); p(c,11,3,g)
    p(c,3,4,g)

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
