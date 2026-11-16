#!/usr/bin/env python3
"""Generator cho sprite "poison-arrow": mũi tên độc (hệ cung).

  fly/fly_right  4 frame lặp: bay sang phải;
  fly_left       4 frame lặp: bay sang trái;
  fly_up         4 frame lặp: bay lên trên;
  fly_down       4 frame lặp: bay xuống dưới;
  impact         6 frame một lần: cắm và bùng vũng độc.

4 hướng bay cho game top-down. Neo tâm (sprite vuông 20x20).

Chạy:  gamekit art run poison-arrow
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

NAME="poison-arrow"; SW,SH=20,8; S=20; OX,OY=(S-SW)//2,(S-SH)//2
ANCHOR=(10.0,10.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#6b5a2e"; TIP="#b8ff66"; TIP_D="#4fa83a"; POI="#7dff5a"; POI_D="#2f7a2f"; FEATHER="#4a7a3a"; FEATHER_D="#2f5a22"

def p(c,x,y,col): c.pixel(x,y,col)

def arrow(c,oy=0):
    y=4+oy
    c.line(2,y,14,y,WOOD)
    c.line(14,y,17,y,TIP_D); p(c,18,y,TIP); p(c,17,y-1,TIP_D); p(c,17,y+1,TIP_D)
    c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)

def fly_base(i):
    c=Canvas(SW,SH); oy=(0,-1,0,1)[i]; arrow(c,oy)
    for k,dx in enumerate((0,2,4,6)):
        if (i+k)%2==0: p(c,1-dx,4+oy+(-1 if k%2 else 1),POI if k<2 else POI_D)
    p(c,13,4+oy-1,POI if i%2==0 else POI_D)
    return c

def impact_base(i):
    c=Canvas(SW,SH); y=4
    if i<=1:
        c.line(2,y,14,y,WOOD); c.line(14,y,16,y+(0 if i==0 else 1),TIP_D)
        c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)
        if i==1:
            for dx,dy in ((17,3),(18,4),(17,5)): p(c,dx,dy,POI)
        return c
    c.line(2,y,13,y,WOOD); c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)
    r = i-1
    for dx,dy in ((14,4),(16,3),(16,5),(18,4),(15,2),(15,6),(17,2),(17,6)):
        if abs(dx-15)+abs(dy-4) <= r+1: p(c,dx,dy,POI if (dx+dy)%2==0 else POI_D)
    if i>=4: p(c,19,4,POI_D)
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
    ("fly",[fly_dir("right",i) for i in range(4)],14,True),
    ("fly_right",[fly_dir("right",i) for i in range(4)],14,True),
    ("fly_left",[fly_dir("left",i) for i in range(4)],14,True),
    ("fly_up",[fly_dir("up",i) for i in range(4)],14,True),
    ("fly_down",[fly_dir("down",i) for i in range(4)],14,True),
    ("impact",[centered(impact_base(i)) for i in range(6)],12,False),
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
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1] if n.startswith("fly") else [0, min(2, len(f)-1)]}}
                     for n, f, fps, lp in ANIMATIONS],
                    anchor=ANCHOR)
    print(OUT/"preview.png")

if __name__=="__main__": main()
