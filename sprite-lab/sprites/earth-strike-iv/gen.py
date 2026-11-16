#!/usr/bin/env python3
"""Landslide IV — sạt lở: đá lăn chéo xuống phải, vệt bụi, KHÔNG xoáy.

DNA: ĐẤT — đứt gãy lệch trục, dịch chuyển khối, nặng, bụi, magma lộ ra.
Không dùng cấu trúc đối xứng tròn/kết tinh của dòng băng.
"""
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

ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"; STRATA="#6e503c"
CRACK="#2b2028"; SHADOW="#1e161c"; DUST="#c9a882"; SAND="#a9815c"
MAGMA="#ff6a2a"; MAGMA_D="#b8331a"; GLOW="#ffd08a"; ASH="#6b5a52"

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def poly(c,pts,col):
    c.polygon([(int(round(a)),int(round(b))) for a,b in pts],col)

def line(c,x1,y1,x2,y2,col,w=1):
    c.line(int(round(x1)),int(round(y1)),int(round(x2)),int(round(y2)),col,w)

def chip(c,x,y,s,hi=True):
    poly(c,[(x,y-s),(x+s,y),(x,y+s),(x-s,y)],ROCK if hi else ROCK_D)
    poly(c,[(x,y-s),(x+s,y),(x,y),(x-s,y)],ROCK_L if hi else SHADOW)
    p(c,x,y,GLOW if hi else STRATA)

def dust(c,x,y,r,col):
    for k in range(6):
        a=k*math.pi/3
        p(c,x+math.cos(a)*r,y+math.sin(a)*r,col)

# IV: sạt lở — đá lăn theo hướng chéo xuống phải, để lại vệt bụi, KHÔNG xoáy.
BOULDERS=[(-18,-14,3),(-9,-11,2),(-2,-16,3),(7,-9,2),(-13,-4,2),(-4,-3,3),(5,-2,2),(13,-5,2)]

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    # đám bụi khởi phát ở góc trái
    dx=CX-15; dy=CY-11
    for rr in range(3,10,2):
        for k in range(10):
            a=k*math.pi/5+i*0.1
            p(c,dx+math.cos(a)*(rr+k%3),dy+math.sin(a)*(rr*0.7+k%2),ASH if rr<7 else DUST)
    # vệt quệt trên mặt đất
    for s in range(6):
        x=CX-16+s*6; y=CY-13+s*5
        for w in range(3):
            p(c, x, y+w, CRACK if w<2 else STRATA)
        p(c,x+2,y+4,DUST)
    # đá lăn dần theo hướng xuống-phải
    for k,(ox,oy,sz) in enumerate(BOULDERS):
        travel=min(1,t*(1.15-k*0.04))
        x=CX+ox+travel*(14+k%3*3)
        y=CY+oy+travel*(12+k%2*2)
        # vệt mờ phía sau
        for s in range(1,4):
            p(c,x-s*2,y-s*2,ASH if s<3 else DUST)
        chip(c,x,y,sz,hi=(k%2==0))
    if i>=4:
        for k in range(10):
            a=k*0.63+i*0.3
            p(c,CX+math.cos(a)*(14+k%5),CY+math.sin(a)*(12+k%4),DUST)
    if i==7:
        for k in range(6): p(c,CX-6+k*5,CY+3+k*3,ROCK_D)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],12,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
