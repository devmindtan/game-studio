#!/usr/bin/env python3
"""Generator cho sprite "hunter-snare": bẫy dây leo trồi lên từ mặt đất (skill cung, AOE khống chế).

  snare   8 frame một lần: mặt đất rung, dây leo gai mọc lên trói vùng mục tiêu
          rồi siết chặt.

Neo (24, 40) tại tâm mặt đất (sprite 48x44). Hiệu ứng mọc từ dưới lên.

Chạy:  gamekit art run hunter-snare
"""

import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="hunter-snare"; W,H=48,44; CX,GY=24,40; ANCHOR=(float(CX),float(GY)); HERE=Path(__file__).resolve().parent; OUT=HERE
VINE="#3f7a2f"; VINE_D="#28501e"; VINE_L="#6fb84a"; THORN="#c9a45a"; GROUND="#5a4a3a"; DUST="#b08a5a"

def p(c,x,y,col):
    if 0<=x<W and 0<=y<H: c.pixel(x,y,col)

def ground(c):
    c.line(4,GY,W-5,GY,GROUND)

def vine(c,x,top_y,lean=0,thorns=True):
    y=GY
    cx=x
    while y>=top_y:
        p(c,cx,y,VINE)
        if (GY-y)%3==0: p(c,cx+1,y,VINE_D)
        if (GY-y)%4==2: cx+= (1 if ((GY-y)//4+lean)%2==0 else -1)
        if thorns and (GY-y)%5==0 and y<GY-2:
            p(c,cx-1,y,THORN); p(c,cx+2,y,THORN)
        y-=1
    p(c,cx,top_y,VINE_L); p(c,cx+1,top_y,VINE_L)

def snare(i):
    c=Canvas(W,H); ground(c)
    bases=[10,17,24,31,38]
    if i==0:
        for b in bases: p(c,b,GY-1,VINE_D); p(c,b+1,GY-1,VINE_D)
        for x in (12,20,28,36): p(c,x,GY-2,DUST)
        return c
    if i==1:
        for b in bases: vine(c,b,GY-6,lean=b%3,thorns=False)
        for x in (8,40): p(c,x,GY-4,DUST)
        return c
    if i==2:
        for k,b in enumerate(bases): vine(c,b,GY-14-k%3,lean=k,thorns=True)
        return c
    if i==3:
        for k,b in enumerate(bases): vine(c,b,GY-22-k%4,lean=k,thorns=True)
        # loops forming
        c.line(12,GY-18,22,GY-20,VINE_L); c.line(26,GY-20,36,GY-18,VINE_L)
        return c
    if i==4:
        for k,b in enumerate(bases): vine(c,b,GY-26,lean=k,thorns=True)
        c.line(10,GY-22,38,GY-22,VINE); c.line(12,GY-16,36,GY-16,VINE_L)
        c.line(14,GY-24,34,GY-24,VINE_D)
        return c
    if i==5:
        for k,b in enumerate(bases): vine(c,b,GY-24,lean=k,thorns=True)
        c.line(10,GY-20,38,GY-20,VINE); c.line(12,GY-14,36,GY-14,VINE_L)
        c.line(14,GY-22,34,GY-22,VINE); c.line(18,GY-18,30,GY-18,VINE_D)
        for b in bases: p(c,b,GY-24,THORN)
        return c
    if i==6:
        for k,b in enumerate(bases): vine(c,b,GY-20,lean=k,thorns=True)
        c.line(11,GY-16,37,GY-16,VINE_D); c.line(13,GY-12,35,GY-12,VINE)
        c.line(15,GY-18,33,GY-18,VINE)
        return c
    # settling
    for k,b in enumerate(bases): vine(c,b,GY-16,lean=k,thorns=True)
    c.line(12,GY-12,36,GY-12,VINE_D); c.line(14,GY-14,34,GY-14,VINE)
    return c

ANIMATIONS=[("snare",[snare(i) for i in range(8)],11,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=4)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=4)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp,"hitbox":{"shape":"rect","center":[float(ANCHOR[0]),float(ANCHOR[1])],"active":[0,len(f)-1]}} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
