#!/usr/bin/env python3
"""Generator cho sprite "arrow-rain": mưa tên từ trên trời xuống (skill cung, AOE).

  rain    10 frame một lần: mũi tên rơi dọc từ trên xuống vùng mục tiêu, cắm đất
          liên tiếp và bụi nổ lên.

Neo (24, 52) tại tâm vùng mặt đất (sprite 48x56). Rơi từ trên cao xuống.

Chạy:  gamekit art run arrow-rain
"""

import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="arrow-rain"; W,H=48,56; CX,GY=24,52; ANCHOR=(float(CX),float(GY)); HERE=Path(__file__).resolve().parent; OUT=HERE
WOOD="#8a5a2e"; STEEL="#c5d4e6"; TIP="#e8f4ff"; FEATHER="#d94a4a"; DUST="#b08a5a"; GROUND="#5a4a3a"

def p(c,x,y,col): c.pixel(x,y,col)

def falling_arrow(c,x,y,phase=0):
    # arrow pointing down (diagonal slight)
    if y<0 or y>GY+2: return
    # shaft
    c.line(x,y-6,x+1,y,WOOD)
    c.line(x,y-5,x+1,y-1,WOOD)
    # tip down
    c.line(x+1,y,x+1,y+2,STEEL); p(c,x+1,y+3,TIP)
    # fletch up
    p(c,x,y-7,FEATHER); p(c,x-1,y-6,FEATHER); p(c,x+1,y-6,FEATHER)

def stuck_arrow(c,x):
    c.line(x,GY-6,x+1,GY-1,WOOD); c.line(x+1,GY-1,x+1,GY+1,STEEL)
    p(c,x,GY-7,FEATHER); p(c,x-1,GY-6,FEATHER)

def rain(i):
    c=Canvas(W,H)
    # target zone hint
    c.ellipse(CX-14,GY-1,CX+14,GY+1,"#b08a5a33")
    c.line(CX-16,GY,CX+16,GY,GROUND)
    drops=[(12,0),(24,2),(36,1),(18,4),(30,3),(8,5),(40,4),(20,6),(28,5),(14,7),(34,6),(22,8)]
    for k,(x,ph) in enumerate(drops):
        # each arrow starts falling at different frames
        start = ph
        t = i - start
        if t < 0: continue
        if t <= 4:
            y = 2 + t*11
            falling_arrow(c,x,y)
            if t>=3: c.ellipse(x-2,GY-1,x+2,GY,"#b08a5a44")
        else:
            # stuck
            stuck_arrow(c,x)
            if t==5:
                for dx,dy in ((-2,-2),(2,-3),(0,-2)): p(c,x+dx,GY+dy,DUST)
            elif t==6:
                for dx,dy in ((-3,-3),(3,-3)): p(c,x+dx,GY+dy,DUST)
    # dust from impacts
    if i>=4:
        for dx in (-10,0,10):
            if (i+dx)%3==0: p(c,CX+dx,GY-2-i%2,DUST)
    return c

ANIMATIONS=[("rain",[rain(i) for i in range(10)],12,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=3)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=3)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
