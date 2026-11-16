#!/usr/bin/env python3
"""Generator cho sprite "piercing-arrow": mũi tên xuyên giáp (hệ cung).

  fly     4 frame lặp: tên nặng bay nhanh, vệt khí phía sau;
  impact  5 frame một lần: xuyên thấu, tia sáng xé gió.

Neo (23, 5) tại đầu mũi (sprite 26x10). Bay sang phải.
"""

import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="piercing-arrow"; W,H=26,10; ANCHOR=(23.0,5.0); HERE=Path(__file__).resolve().parent; OUT=HERE
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

def fly(i):
    c=Canvas(W,H); bolt(c, oy=(0,-1,0,1)[i], trail=i+1)
    return c

def impact(i):
    c=Canvas(W,H)
    if i==0:
        bolt(c); 
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

ANIMATIONS=[("fly",[fly(i) for i in range(4)],18,True),("impact",[impact(i) for i in range(5)],15,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=7)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=7)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
