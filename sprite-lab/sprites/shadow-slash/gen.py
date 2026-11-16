#!/usr/bin/env python3
"""Nhát chém bóng tối (hệ sát thủ, AOE): vệt chém nhanh kèm bóng tím.

  slash   6 frame một lần: vệt chém xẹt qua theo cung.

Neo (8, 24) điểm xuất phát (sprite 48x48). Chém sang phải.
"""
import sys,math
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="shadow-slash"; S=48; ANCHOR=(8.0,24.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CORE="#f5d0fe"; EDGE="#d946ef"; DARK="#6b21a8"; SHADOW="#2a1038"
def p(c,x,y,col):
    if 0<=x<S and 0<=y<S: c.pixel(x,y,col)
def arc(c,cx,cy,r,a0,a1,col,step=3,th=1):
    a=a0
    while a<=a1:
        rad=math.radians(a)
        for t in range(th):
            rr=r-t
            p(c,round(cx+math.cos(rad)*rr),round(cy+math.sin(rad)*rr),col)
        a+=step
def slash(i):
    c=Canvas(S,S); ox,oy=8,24
    if i==0:
        arc(c,ox,oy,14,-50,0,DARK,4,2); p(c,18,18,EDGE); return c
    if i==1:
        arc(c,ox,oy,22,-65,30,SHADOW,3,4); arc(c,ox,oy,20,-60,25,DARK,3,2); arc(c,ox,oy,18,-55,20,EDGE,3,1)
        return c
    if i==2:
        arc(c,ox,oy,28,-70,50,SHADOW,3,4); arc(c,ox,oy,26,-65,45,DARK,3,3); arc(c,ox,oy,23,-60,40,EDGE,3,2); arc(c,ox,oy,20,-50,30,CORE,3,1)
        return c
    if i==3:
        arc(c,ox,oy,32,-60,55,DARK,3,3); arc(c,ox,oy,29,-50,45,EDGE,3,2); arc(c,ox,oy,26,-40,35,CORE,3,1)
        for dx,dy in ((30,14),(34,24),(30,34)): p(c,ox+dx-8,oy+dy-24,EDGE)
        return c
    if i==4:
        arc(c,ox,oy,34,-40,45,DARK,4,2); arc(c,ox,oy,31,-30,35,EDGE,4,1)
        return c
    arc(c,ox,oy,34,-20,30,DARK,5,1)
    return c
ANIMATIONS=[("slash",[slash(i) for i in range(6)],16,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*S,len(ANIMATIONS)*S)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*S)
    preview([sheet],HERE/"preview.png",scale=4)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=4)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
