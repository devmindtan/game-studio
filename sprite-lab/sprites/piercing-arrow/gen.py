#!/usr/bin/env python3
"""Generator cho sprite "piercing-arrow": mũi tên xuyên giáp (hệ cung).

  fly/fly_right  4 frame lặp: bay sang phải;
  fly_left       4 frame lặp: bay sang trái;
  fly_up         4 frame lặp: bay lên trên;
  fly_down       4 frame lặp: bay xuống dưới;
  impact         5 frame một lần: xuyên thấu, tia sáng xé gió.

4 hướng bay cho game top-down. Neo tâm (sprite vuông 26x26).

Chạy:  gamekit art run piercing-arrow
"""

import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
from PIL import Image

NAME="piercing-arrow"; SW,SH=26,10; S=26; OX,OY=(S-SW)//2,(S-SH)//2
ANCHOR=(13.0,13.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#6b4a2e"; STEEL="#d7e6f5"; TIP="#ffffff"; EDGE="#8ad8ff"; FEATHER="#4a6fa8"; FEATHER_D="#2f4f7a"

def p(c,x,y,col): c.pixel(x,y,col)

def bolt(c,oy=0,trail=0):
    y=5+oy
    c.line(3,y,18,y,WOOD,2); c.line(3,y,17,y,"#4a3524",1)
    c.line(18,y,22,y,STEEL,2); c.line(19,y-1,22,y,EDGE); c.line(19,y+1,22,y,EDGE)
    p(c,23,y,TIP); p(c,22,y-1,TIP)
    c.polygon([(3,y),(6,y-3),(7,y)],FEATHER); c.polygon([(3,y),(6,y+3),(7,y)],FEATHER_D)
    if trail:
        for i,dx in enumerate((0,2,4,6,8)):
            if (trail+i)%2==0: p(c,2-dx,y+(-1 if i%2 else 0),EDGE)

def fly_base(i):
    c=Canvas(SW,SH); bolt(c, oy=(0,-1,0,1)[i], trail=i+1)
    return c

def impact_base(i):
    c=Canvas(SW,SH)
    if i==0:
        bolt(c)
        for dx,dy in ((24,4),(24,6),(25,5)): p(c,dx,dy,TIP)
        return c
    if i==1:
        y=5; c.line(3,y,20,y,WOOD,2); c.line(20,y,24,y,STEEL,2); p(c,24,y,TIP)
        c.polygon([(3,y),(6,y-3),(7,y)],FEATHER); c.polygon([(3,y),(6,y+3),(7,y)],FEATHER_D)
        c.line(22,3,25,2,EDGE); c.line(22,7,25,8,EDGE)
        return c
    y=5
    c.line(3,y,21,y,WOOD,2); c.line(21,y,24,y,STEEL)
    c.polygon([(3,y),(6,y-3),(7,y)],FEATHER); c.polygon([(3,y),(6,y+3),(7,y)],FEATHER_D)
    if i==2:
        p(c,25,3,EDGE); p(c,25,7,EDGE); p(c,25,5,TIP)
    elif i==3:
        p(c,25,4,EDGE); p(c,25,6,EDGE)
    return c

def centered(base):
    out=Canvas(S,S); out.paste(base,OX,OY); return out

def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc

_SIDE=[centered(fly_base(i)) for i in range(4)]

def fly_dir(direction, i):
    b=_SIDE[i]
    if direction=="right": return b.copy()
    if direction=="up": return rot(b,90)
    if direction=="left": return rot(b,180)
    if direction=="down": return rot(b,270)
    raise ValueError(direction)

ANIMATIONS=[
    ("fly",[fly_dir("right",i) for i in range(4)],18,True),
    ("fly_right",[fly_dir("right",i) for i in range(4)],18,True),
    ("fly_left",[fly_dir("left",i) for i in range(4)],18,True),
    ("fly_up",[fly_dir("up",i) for i in range(4)],18,True),
    ("fly_down",[fly_dir("down",i) for i in range(4)],18,True),
    ("impact",[centered(impact_base(i)) for i in range(5)],15,False),
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
