#!/usr/bin/env python3
"""Frost Nova cấp IV — AOE băng lan tròn, mạnh hơn cấp trước (tầm 30px, 20 mảnh)."""
import math, sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
HERE=Path(__file__).resolve().parent
sys.path.insert(0, str(_ws()/"tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"lib"))
from spritekit import Canvas
from sheet import export

NAME=Path(__file__).parent.name
SIZE=72; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
TIER=4

CORE="#ffffff"; ICE="#c8f6ff"; ICE_M="#6fe0ff"; ICE_D="#2a8fd6"; DEEP="#1b4f8a"
FROST="#9fe8ff"; SNOW="#eaf9ff"

def p(c,x,y,col):
    if 0<=x<SIZE and 0<=y<SIZE: c.pixel(x,y,col)

def ring(c,r,col):
    if r>0: c.ellipse(CX-r,CY-r,CX+r,CY+r,col,fill=False)

def shard(c,x,y,a,col,long=False):
    dx=1 if math.cos(a)>=0 else -1
    dy=1 if math.sin(a)>=0 else -1
    p(c,x,y,col); p(c,x+dx,y,col); p(c,x,y+dy,col)
    if long:
        p(c,x+dx*2,y,col); p(c,x,y+dy*2,col)

def frame(i):
    c=Canvas(SIZE,SIZE)
    # tiến độ nổ 0..1 qua 8 frame
    t=i/7.0
    R=30
    nsh=20
    rings=3

    if i==0:
        c.ellipse(CX-3,CY-3,CX+3,CY+3,ICE_M)
        c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE)
        for k in range(nsh//2):
            a=math.radians(k*360/(nsh//2))
            p(c,round(CX+math.cos(a)*5),round(CY+math.sin(a)*5),ICE)
        return c

    r0=max(2,round(R*0.30*t))
    r1=max(3,round(R*(0.45+0.55*t)))
    # vong trong / ngoai
    ring(c,r0,ICE_M)
    ring(c,r1,ICE_D if i<6 else DEEP)
    if rings>=2 and i>=2: ring(c,max(2,round(r1*0.72)),ICE)
    if rings>=3 and i>=4: ring(c,max(2,round(r1*0.55)),ICE_M)

    # tam lõi
    cr=max(1,round(4*(1-t*0.6)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,ICE if i<5 else ICE_M)
    c.pixel(CX,CY,CORE if i<6 else ICE)

    # mảnh băng bay ra
    for k in range(nsh):
        a=math.radians(k*360/nsh + (7 if i%2 else 0))
        rad=round(r1+(k%3)*2)
        shard(c,round(CX+math.cos(a)*rad),round(CY+math.sin(a)*rad),a,
              ICE if k%3 else FROST, long=(TIER>=3 and k%2==0))

    # cap cao: mat bang đóng băng + tia băng dài + tuyết
    if TIER>=2:
        for k in range(20):
            a=math.radians(k*360/20 + (i*3))
            x=round(CX+math.cos(a)*r1*0.6); y=round(CY+math.sin(a)*r1*0.6)
            p(c,x,y,ICE)
    if TIER>=3:
        for k in range(nsh//2):
            a=math.radians(k*720/nsh + 15)
            rad=round(r1*0.85)
            x=round(CX+math.cos(a)*rad); y=round(CY+math.sin(a)*rad)
            p(c,x,y,DEEP); p(c,x+1,y,ICE_D)
    if TIER>=4:
        for k in range(10):
            a=math.radians(k*137+i*19); rad=round(r1*(0.5+((k%5)/10)))
            p(c,round(CX+math.cos(a)*rad),round(CY+math.sin(a)*rad),SNOW)
    if TIER>=5:
        ring(c,max(1,round(r1*0.35)),CORE if i<6 else ICE)
        for k in range(8):
            a=math.radians(k*45+i*5)
            rad=round(r1*1.12)
            p(c,round(CX+math.cos(a)*rad),round(CY+math.sin(a)*rad),CORE)
    if i==7:
        # tàn: vài mảnh rơi
        for k in range(6):
            a=math.radians(k*60+12)
            p(c,round(CX+math.cos(a)*(R-2)),round(CY+math.sin(a)*(R-2)),DEEP)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],12,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
