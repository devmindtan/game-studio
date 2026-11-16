#!/usr/bin/env python3
"""Icon trạng thái "status-stun": choáng (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-stun
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-stun"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    y="#ffd84a"; yd="#b88900"; w="#ffffff"
    # stars spinning
    def star(cx,cy,col):
        for dx,dy in [(0,-2),(0,2),(-2,0),(2,0),(-1,-1),(1,-1),(-1,1),(1,1),(0,0)]:
            p(c,cx+dx,cy+dy,col)
    star(5,6,y); star(11,6,yd); star(8,10,y)
    p(c,5,6,w); p(c,11,6,w); p(c,8,10,w)

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
