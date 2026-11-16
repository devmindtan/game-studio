#!/usr/bin/env python3
"""Generator cho sprite "scatter-volley": loạt tên tỏa quạt phía trước (skill cung, AOE).

  volley/volley_right  7 frame một lần: bắn sang phải;
  volley_left          7 frame một lần: bắn sang trái;
  volley_up            7 frame một lần: bắn lên trên;
  volley_down          7 frame một lần: bắn xuống dưới.

AOE định hướng cho game top-down. Neo tâm (sprite 48x48).

Chạy:  gamekit art run scatter-volley
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

NAME="scatter-volley"; S=48; ANCHOR=(24.0,24.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#8a5a2e"; STEEL="#c5d4e6"; TIP="#e8f4ff"; FEATHER="#d94a4a"; WIND="#cfe8ff"

def p(c,x,y,col):
    if 0<=x<S and 0<=y<S: c.pixel(x,y,col)

def arrow_at(c,ox,oy,ang,length=10,tip=True):
    rad=math.radians(ang)
    x1=ox+length*math.cos(rad); y1=oy+length*math.sin(rad)
    c.line(round(ox),round(oy),round(x1),round(y1),WOOD)
    tx=ox+(length+3)*math.cos(rad); ty=oy+(length+3)*math.sin(rad)
    c.line(round(x1),round(y1),round(tx),round(ty),STEEL)
    if tip: p(c,round(tx+math.cos(rad)),round(ty+math.sin(rad)),TIP)
    bx=ox+2*math.cos(rad); by=oy+2*math.sin(rad)
    px=2*math.cos(rad+1.57); py=2*math.sin(rad+1.57)
    c.line(round(bx),round(by),round(bx-px*1.5),round(by-py*1.5),FEATHER)
    c.line(round(bx),round(by),round(bx+px*1.5),round(by+py*1.5),FEATHER)

def volley_base(i):
    c=Canvas(S,S)
    ox,oy=4,24
    angles=[-30,-15,-5,5,15,30]
    if i==0:
        for a in angles: arrow_at(c,ox+2,oy,a,4)
        p(c,6,24,WIND); p(c,5,22,WIND); p(c,5,26,WIND)
        return c
    dist = 4 + i*6
    for k,a in enumerate(angles):
        d = dist - (k%2)
        if d<0: continue
        rad=math.radians(a)
        ax=ox + d*math.cos(rad); ay=oy + d*math.sin(rad)
        if ax < S-1:
            arrow_at(c,round(ax),round(ay),a,8)
            bx=ax-10*math.cos(rad); by=ay-10*math.sin(rad)
            if (i+k)%2==0 and bx>ox: p(c,round(bx),round(by),WIND)
    if i>=4:
        for a in (-20,0,20):
            rad=math.radians(a); fx=ox+(dist+10)*math.cos(rad); fy=oy+(dist+10)*math.sin(rad)
            if 0<fx<S-1 and 0<fy<S-1: p(c,round(fx),round(fy),TIP)
    return c

def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc

_SIDE=[volley_base(i) for i in range(7)]

def dir_frames(base_frames, direction):
    if direction=="right": return [f.copy() for f in base_frames]
    if direction=="up": return [rot(f,90) for f in base_frames]
    if direction=="left": return [rot(f,180) for f in base_frames]
    if direction=="down": return [rot(f,270) for f in base_frames]
    raise ValueError(direction)

ANIMATIONS=[
    ("volley",dir_frames(_SIDE,"right"),15,False),
    ("volley_right",dir_frames(_SIDE,"right"),15,False),
    ("volley_left",dir_frames(_SIDE,"left"),15,False),
    ("volley_up",dir_frames(_SIDE,"up"),15,False),
    ("volley_down",dir_frames(_SIDE,"down"),15,False),
]

def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*S,len(ANIMATIONS)*S)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*S)
    preview([sheet],HERE/"preview.png",scale=4)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=4)
    dir_map = {"volley":0.0,"volley_right":0.0,"volley_left":180.0,"volley_up":-90.0,"volley_down":90.0}
    meta_anims = []
    for n,f,fps,lp in ANIMATIONS:
        meta_anims.append({"name":n,"frames":f,"fps":fps,"loop":lp,
                           "hitbox":{"shape":"arc","center":[float(ANCHOR[0]),float(ANCHOR[1])],
                                     "active":[1,len(f)-1],"dir_deg":dir_map.get(n,0.0)}})
    write_anim_meta(OUT/f"{NAME}.json", meta_anims, anchor=ANCHOR)
    print(OUT/"preview.png")

if __name__=="__main__": main()
