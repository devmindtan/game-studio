#!/usr/bin/env python3
"""Generator cho sprite "poison-arrow": mũi tên độc (hệ cung).

  fly     4 frame lặp: tên tẩm độc, vệt khói xanh lục;
  impact  6 frame một lần: cắm và bùng vũng độc.

Neo (17, 4) tại đầu mũi (sprite 20x8). Bay sang phải.
"""

import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="poison-arrow"; W,H=20,8; ANCHOR=(17.0,4.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#6b5a2e"; TIP="#b8ff66"; TIP_D="#4fa83a"; POI="#7dff5a"; POI_D="#2f7a2f"; FEATHER="#4a7a3a"; FEATHER_D="#2f5a22"
def p(c,x,y,col): c.pixel(x,y,col)

def arrow(c,oy=0):
    y=4+oy
    c.line(2,y,14,y,WOOD)
    c.line(14,y,17,y,TIP_D); p(c,18,y,TIP); p(c,17,y-1,TIP_D); p(c,17,y+1,TIP_D)
    c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)

def fly(i):
    c=Canvas(W,H); oy=(0,-1,0,1)[i]; arrow(c,oy)
    # poison trail
    for k,dx in enumerate((0,2,4,6)):
        if (i+k)%2==0: p(c,1-dx,4+oy+(-1 if k%2 else 1),POI if k<2 else POI_D)
    p(c,13,4+oy-1,POI if i%2==0 else POI_D)
    return c

def impact(i):
    c=Canvas(W,H); y=4
    if i<=1:
        c.line(2,y,14,y,WOOD); c.line(14,y,16,y+(0 if i==0 else 1),TIP_D)
        c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)
        if i==1:
            for dx,dy in ((17,3),(18,4),(17,5)): p(c,dx,dy,POI)
        return c
    # poison splash
    c.line(2,y,13,y,WOOD); c.line(2,y,4,y-2,FEATHER); c.line(2,y,4,y+2,FEATHER_D)
    r = i-1
    for dx,dy in ((14,4),(16,3),(16,5),(18,4),(15,2),(15,6),(17,2),(17,6)):
        if abs(dx-15)+abs(dy-4) <= r+1: p(c,dx,dy,POI if (dx+dy)%2==0 else POI_D)
    if i>=4: p(c,19,4,POI_D)
    return c

ANIMATIONS=[("fly",[fly(i) for i in range(4)],14,True),("impact",[impact(i) for i in range(6)],12,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=8)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=8)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
