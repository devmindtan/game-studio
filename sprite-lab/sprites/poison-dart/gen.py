#!/usr/bin/env python3
"""Phi tiêu độc (hệ sát thủ): projectile nhỏ, nhanh, tẩm độc.

  fly     4 frame lặp: phi tiêu bay thẳng với vệt độc;
  impact  5 frame một lần: trúng và lan độc.

Neo (15, 4) đầu (sprite 18x8). Bay sang phải.
"""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="poison-dart"; W,H=18,8; ANCHOR=(15.0,4.0); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#4a3524"; TIP="#b8ff66"; TIP_D="#4fa83a"; POI="#7dff5a"; POI_D="#2f7a2f"; FEATHER="#7a4f8a"
def p(c,x,y,col): c.pixel(x,y,col)
def dart(c,oy=0):
    y=4+oy
    c.line(3,y,12,y,WOOD); c.line(12,y,15,y,TIP_D); p(c,16,y,TIP)
    p(c,3,y-1,FEATHER); p(c,3,y+1,FEATHER); p(c,2,y,FEATHER)
def fly(i):
    c=Canvas(W,H); oy=(0,-1,0,1)[i]; dart(c,oy)
    for k,dx in enumerate((1,3,5)):
        if (i+k)%2==0: p(c,2-dx,4+oy,POI if k==0 else POI_D)
    return c
def impact(i):
    c=Canvas(W,H); y=4
    if i==0: dart(c); p(c,17,y,POI); return c
    c.line(3,y,13,y,WOOD); c.line(13,y,15,y,TIP_D); p(c,3,y-1,FEATHER); p(c,3,y+1,FEATHER)
    r=i
    for dx,dy in ((16,4),(17,3),(17,5),(18,4),(16,2),(16,6)):
        if abs(dx-16)+abs(dy-4)<=r: p(c,dx,dy,POI if (dx+dy)%2==0 else POI_D)
    return c
ANIMATIONS=[("fly",[fly(i) for i in range(4)],18,True),("impact",[impact(i) for i in range(5)],13,False)]
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
