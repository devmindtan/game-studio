#!/usr/bin/env python3
"""Generator cho sprite "scatter-volley": loạt tên tỏa quạt phía trước (skill cung, AOE).

  volley  7 frame một lần: chùm mũi tên bắn ra tỏa hình quạt về phía trước,
          xuyên qua vùng ảnh hưởng.

Neo (4, 24) tại điểm bắn bên trái (sprite 48x48). Bắn sang phải.

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
NAME="scatter-volley"; W,H=48,48; ANCHOR=(4.0,24.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#8a5a2e"; STEEL="#c5d4e6"; TIP="#e8f4ff"; FEATHER="#d94a4a"; WIND="#cfe8ff"

def p(c,x,y,col):
    if 0<=x<W and 0<=y<H: c.pixel(x,y,col)

def arrow_at(c,ox,oy,ang,length=10,tip=True):
    # ang in degrees, 0 = right
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

def volley(i):
    c=Canvas(W,H)
    ox,oy=4,24
    angles=[-30,-15,-5,5,15,30]
    if i==0:
        # release flash
        for a in angles: arrow_at(c,ox+2,oy,a,4)
        p(c,6,24,WIND); p(c,5,22,WIND); p(c,5,26,WIND)
        return c
    # arrows travel outward
    dist = 4 + i*6
    for k,a in enumerate(angles):
        # slight stagger
        d = dist - (k%2)
        if d<0: continue
        rad=math.radians(a)
        ax=ox + d*math.cos(rad); ay=oy + d*math.sin(rad)
        if ax < W-1:
            arrow_at(c,round(ax),round(ay),a,8)
            # trail
            bx=ax-10*math.cos(rad); by=ay-10*math.sin(rad)
            if (i+k)%2==0 and bx>ox: p(c,round(bx),round(by),WIND)
    if i>=4:
        # leading impacts/sparkles at front
        for a in (-20,0,20):
            rad=math.radians(a); fx=ox+(dist+10)*math.cos(rad); fy=oy+(dist+10)*math.sin(rad)
            if 0<fx<W-1 and 0<fy<H-1: p(c,round(fx),round(fy),TIP)
    return c

ANIMATIONS=[("volley",[volley(i) for i in range(7)],15,False)]
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
