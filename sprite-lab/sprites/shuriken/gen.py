#!/usr/bin/env python3
"""Phi tiêu shuriken (hệ sát thủ): projectile xoay.

  fly/fly_right  4 frame lặp: bay sang phải;
  fly_left       4 frame lặp: bay sang trái;
  fly_up         4 frame lặp: bay lên trên;
  fly_down       4 frame lặp: bay xuống dưới;
  impact         5 frame một lần: găm và lóe tia.

4 hướng bay cho game top-down. Neo tâm (sprite 16x16).

Chạy:  gamekit art run shuriken
"""
import sys, math
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
from PIL import Image

NAME="shuriken"; S=16; ANCHOR=(8.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE
STEEL="#d7e6f5"; EDGE="#ffffff"; DARK="#5f7187"

def p(c,x,y,col):
    if 0<=x<S and 0<=y<S: c.pixel(x,y,col)

def star(c,cx,cy,rot):
    for k in range(4):
        a=math.radians(rot+k*90)
        for t in range(1,7):
            x=cx+t*math.cos(a); y=cy+t*math.sin(a)
            col=EDGE if t>4 else STEEL if t>2 else DARK
            p(c,round(x),round(y),col)
        a2=a+0.35
        for t in range(2,5):
            x=cx+t*math.cos(a2); y=cy+t*math.sin(a2); p(c,round(x),round(y),DARK)
    c.rect(cx-1,cy-1,cx+1,cy+1,DARK); p(c,cx,cy,EDGE)

def fly_side(i):
    c=Canvas(S,S); star(c,8,8,i*45)
    # trail phía sau (trái) khi bay sang phải
    if i%2==0: p(c,1,8,DARK)
    else: p(c,0,8,DARK)
    return c

def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc

def fly_dir(direction, i):
    base = fly_side(i)
    if direction == "right": return base
    if direction == "up": return rot(base, 90)
    if direction == "left": return rot(base, 180)
    if direction == "down": return rot(base, 270)
    raise ValueError(direction)

def impact(i):
    c=Canvas(S,S)
    if i==0: star(c,8,8,20); p(c,14,8,EDGE); return c
    star(c,9,8,45)
    if i==1:
        for dx,dy in ((14,7),(14,9),(13,6),(13,10)): p(c,dx,dy,STEEL)
    elif i==2:
        p(c,14,7,STEEL); p(c,14,9,STEEL)
    return c

ANIMATIONS=[
    ("fly",[fly_dir("right",i) for i in range(4)],18,True),
    ("fly_right",[fly_dir("right",i) for i in range(4)],18,True),
    ("fly_left",[fly_dir("left",i) for i in range(4)],18,True),
    ("fly_up",[fly_dir("up",i) for i in range(4)],18,True),
    ("fly_down",[fly_dir("down",i) for i in range(4)],18,True),
    ("impact",[impact(i) for i in range(5)],14,False),
]

def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*S,len(ANIMATIONS)*S)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*S)
    preview([sheet],HERE/"preview.png",scale=6)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=6)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name":n,"frames":f,"fps":fps,"loop":lp,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1] if n.startswith("fly") else [0, len(f)-1]}}
                     for n, f, fps, lp in ANIMATIONS],
                    anchor=ANCHOR)
    print(OUT/"preview.png")

if __name__=="__main__": main()
