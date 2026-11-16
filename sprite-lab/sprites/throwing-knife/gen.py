#!/usr/bin/env python3
"""Dao phóng (hệ sát thủ): projectile xoay bay và cắm trúng.

  fly     4 frame lặp: dao xoay khi bay;
  impact  5 frame một lần: cắm và tia lửa.

Neo (10, 8) tâm (sprite 20x16). Bay sang phải.
"""
import sys,math
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="throwing-knife"; W,H=20,16; ANCHOR=(10.0,8.0); HERE=Path(__file__).resolve().parent; OUT=HERE
STEEL="#d7e6f5"; EDGE="#ffffff"; DARK="#5f7187"; HANDLE="#3a2a38"; WRAP="#8b3a62"
def p(c,x,y,col):
    if 0<=x<W and 0<=y<H: c.pixel(x,y,col)
def knife(c,cx,cy,ang):
    rad=math.radians(ang)
    # blade
    for t in range(-5,7):
        x=cx+t*math.cos(rad); y=cy+t*math.sin(rad)
        col=EDGE if t>4 else STEEL if t>-2 else DARK
        p(c,round(x),round(y),col)
        if -2<t<5: p(c,round(x-math.sin(rad)),round(y+math.cos(rad)),DARK)
    # handle
    for t in range(-7,-4):
        x=cx+t*math.cos(rad); y=cy+t*math.sin(rad)
        p(c,round(x),round(y),HANDLE); p(c,round(x-math.sin(rad)),round(y+math.cos(rad)),WRAP)
def fly(i):
    c=Canvas(W,H); knife(c,10,8,i*90)
    if i%2==0: p(c,2,8,DARK)
    return c
def impact(i):
    c=Canvas(W,H)
    if i==0: knife(c,10,8,0); p(c,18,8,EDGE); return c
    if i==1:
        # stuck
        c.line(4,8,14,8,DARK); c.line(5,8,15,8,STEEL); c.line(15,8,17,8,EDGE)
        c.rect(3,7,5,9,HANDLE); p(c,4,8,WRAP)
        for dx,dy in ((18,7),(18,9),(19,8)): p(c,dx,dy,STEEL); return c
    c.line(4,8,14,8,DARK); c.line(5,8,15,8,STEEL); c.line(15,8,17,8,EDGE)
    c.rect(3,7,5,9,HANDLE); p(c,4,8,WRAP)
    if i==2: p(c,18,7,STEEL); p(c,18,9,STEEL)
    if i==3: p(c,19,8,DARK)
    return c
ANIMATIONS=[("fly",[fly(i) for i in range(4)],16,True),("impact",[impact(i) for i in range(5)],14,False)]
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
