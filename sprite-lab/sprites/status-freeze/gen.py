#!/usr/bin/env python3
"""Icon trạng thái "status-freeze": đóng băng (debuff) (UI icon tĩnh, 16x16).

Chạy:  gamekit art run status-freeze
"""
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta

NAME="status-freeze"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE

def p(c,x,y,col): c.pixel(x,y,col)


def draw(c):
    ice="#7fdcff"; idk="#2f7fb0"; il="#e6fbff"
    # snowflake
    for i in range(3,13): p(c,8,i,ice); p(c,i,8,ice)
    for d in range(-4,5):
        p(c,8+d,8+d,ice); p(c,8+d,8-d,ice)
    p(c,8,8,il)
    for dx,dy in [(0,-4),(0,4),(-4,0),(4,0),(-3,-3),(3,3),(-3,3),(3,-3)]:
        p(c,8+dx,8+dy,il)
        p(c,8+dx+(-1 if dx>0 else 1 if dx<0 else 0),8+dy+(-1 if dy>0 else 1 if dy<0 else 0),idk)

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
