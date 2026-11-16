#!/usr/bin/env python3
"""Icon trạng thái "status-bleed": chảy máu (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-bleed
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-bleed"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    # red droplet with slash
    drop="#d7263d"; dark="#7a1020"; light="#ff6b81"
    # droplet
    for y in range(4,13):
        w = 1 if y<6 else 2 if y<8 else 3 if y<11 else 2 if y<12 else 1
        x0 = 8-w
        c.rect(x0,y,8+w-1,y,drop)
    c.rect(7,5,8,5,light); c.rect(6,6,7,6,light)
    c.rect(6,11,9,11,dark); p(c,8,12,dark); p(c,7,13,dark)
    # small blood drops
    for x,y in ((3,3),(11,4),(4,11)):
        p(c,x,y,drop); p(c,x,y+1,dark)

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
