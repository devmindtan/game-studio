#!/usr/bin/env python3
"""Bom khói (hệ sát thủ, AOE): nổ và phủ màn khói.

  burst   8 frame một lần: bom nổ, khói lan rộng rồi tan.

Neo (24, 28) tâm vùng khói (sprite 48x40).
"""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="smoke-bomb"; W,H=48,40; CX,CY=24,24; ANCHOR=(24.0,28.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CORE="#d0d8e8"; SMOKE="#8a96aa"; SMOKE_D="#556070"; SMOKE_L="#b8c4d8"; SPARK="#ffd36b"
def p(c,x,y,col):
    if 0<=x<W and 0<=y<H: c.pixel(x,y,col)
def cloud(c,cx,cy,rx,ry,col):
    c.ellipse(cx-rx,cy-ry,cx+rx,cy+ry,col)
def burst(i):
    c=Canvas(W,H)
    if i==0:
        cloud(c,CX,CY,3,2,SMOKE_L); p(c,CX,CY,SPARK)
        for dx,dy in ((4,0),(-4,0),(0,3),(0,-3)): p(c,CX+dx,CY+dy,SPARK)
        return c
    if i==1:
        cloud(c,CX,CY,6,4,SMOKE); cloud(c,CX,CY,4,3,SMOKE_L); cloud(c,CX,CY,2,1,CORE)
        for dx,dy in ((7,-2),(-7,1),(3,5),(-4,-4)): p(c,CX+dx,CY+dy,SMOKE_L)
        return c
    if i==2:
        cloud(c,CX-4,CY-1,7,5,SMOKE_D); cloud(c,CX+4,CY+1,7,5,SMOKE_D)
        cloud(c,CX,CY,8,6,SMOKE); cloud(c,CX,CY-1,5,4,SMOKE_L)
        return c
    if i==3:
        cloud(c,CX-6,CY-2,8,6,SMOKE_D); cloud(c,CX+6,CY+1,8,6,SMOKE_D)
        cloud(c,CX,CY,10,7,SMOKE); cloud(c,CX-2,CY-2,6,4,SMOKE_L); cloud(c,CX+5,CY,5,4,SMOKE_L)
        return c
    if i==4:
        cloud(c,CX-7,CY-2,9,7,SMOKE_D); cloud(c,CX+7,CY+1,9,7,SMOKE_D); cloud(c,CX,CY,11,8,SMOKE)
        cloud(c,CX-3,CY-3,6,4,SMOKE_L); cloud(c,CX+4,CY,6,4,SMOKE)
        return c
    if i==5:
        cloud(c,CX-8,CY-1,9,7,SMOKE_D); cloud(c,CX+8,CY+1,9,7,SMOKE_D); cloud(c,CX,CY,10,7,SMOKE)
        for dx,dy in ((-14,0),(14,-2),(0,-8),(0,8)): p(c,CX+dx,CY+dy,SMOKE_D)
        return c
    if i==6:
        cloud(c,CX-6,CY,8,6,SMOKE_D); cloud(c,CX+6,CY,8,6,SMOKE_D); cloud(c,CX,CY,9,6,SMOKE)
        return c
    cloud(c,CX-4,CY,6,4,SMOKE_D); cloud(c,CX+4,CY,6,4,SMOKE_D); cloud(c,CX,CY,7,5,SMOKE_D)
    return c
ANIMATIONS=[("burst",[burst(i) for i in range(8)],10,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=4)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=4)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
