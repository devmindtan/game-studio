#!/usr/bin/env python3
"""Dao phóng (hệ sát thủ): projectile xoay bay và cắm trúng.

  fly/fly_right  4 frame lặp: bay sang phải;
  fly_left       4 frame lặp: bay sang trái;
  fly_up         4 frame lặp: bay lên trên;
  fly_down       4 frame lặp: bay xuống dưới;
  impact         5 frame một lần: cắm và tia lửa.

4 hướng bay cho game top-down. Neo tâm (sprite vuông 20x20).

Chạy:  gamekit art run throwing-knife
"""
import sys,math
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
from PIL import Image

NAME="throwing-knife"; SW,SH=20,16; S=20; OX,OY=(S-SW)//2,(S-SH)//2
ANCHOR=(10.0,10.0); HERE=Path(__file__).resolve().parent; OUT=HERE
STEEL="#d7e6f5"; EDGE="#ffffff"; DARK="#5f7187"; HANDLE="#3a2a38"; WRAP="#8b3a62"

def p(c,x,y,col):
    if 0<=x<SW and 0<=y<SH: c.pixel(x,y,col)

def knife(c,cx,cy,ang):
    rad=math.radians(ang)
    for t in range(-5,7):
        x=cx+t*math.cos(rad); y=cy+t*math.sin(rad)
        col=EDGE if t>4 else STEEL if t>-2 else DARK
        p(c,round(x),round(y),col)
        if -2<t<5: p(c,round(x-math.sin(rad)),round(y+math.cos(rad)),DARK)
    for t in range(-7,-4):
        x=cx+t*math.cos(rad); y=cy+t*math.sin(rad)
        p(c,round(x),round(y),HANDLE); p(c,round(x-math.sin(rad)),round(y+math.cos(rad)),WRAP)

def fly_base(i):
    c=Canvas(SW,SH); knife(c,10,8,i*90)
    if i%2==0: p(c,2,8,DARK)
    return c

def impact_base(i):
    c=Canvas(SW,SH)
    if i==0: knife(c,10,8,0); p(c,18,8,EDGE); return c
    if i==1:
        c.line(4,8,14,8,DARK); c.line(5,8,15,8,STEEL); c.line(15,8,17,8,EDGE)
        c.rect(3,7,5,9,HANDLE); p(c,4,8,WRAP)
        for dx,dy in ((18,7),(18,9),(19,8)): p(c,dx,dy,STEEL); return c
    c.line(4,8,14,8,DARK); c.line(5,8,15,8,STEEL); c.line(15,8,17,8,EDGE)
    c.rect(3,7,5,9,HANDLE); p(c,4,8,WRAP)
    if i==2: p(c,18,7,STEEL); p(c,18,9,STEEL)
    if i==3: p(c,19,8,DARK)
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
    ("fly",[fly_dir("right",i) for i in range(4)],16,True),
    ("fly_right",[fly_dir("right",i) for i in range(4)],16,True),
    ("fly_left",[fly_dir("left",i) for i in range(4)],16,True),
    ("fly_up",[fly_dir("up",i) for i in range(4)],16,True),
    ("fly_down",[fly_dir("down",i) for i in range(4)],16,True),
    ("impact",[centered(impact_base(i)) for i in range(5)],14,False),
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
