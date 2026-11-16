#!/usr/bin/env python3
"""Earth Bloom II — vết nứt hình hoa 8 cánh + nhánh phụ."""
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
SIZE=56; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
TIER=2

# palette đất/đá
ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"
CRACK="#2b2028"; DARK="#1e161c"; HOT="#d98a4a"; GLOW="#ffd08a"
DUST="#c9a882"; SAND="#a9815c"; MAGMA="#ff6a2a"; MAGMA_D="#b8331a"
ASH="#6b5a52"; SMOKE="#3a3038"
FROST="#9fe8ff"  # for V only

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def poly(c,pts,col):
    c.polygon([(int(round(x)),int(round(y))) for x,y in pts],col)

def ring(c,r,col):
    if r>0: c.ellipse(CX-r,CY-r,CX+r,CY+r,col,fill=False)

def dot(c,a,r,col,size=1):
    x=CX+math.cos(a)*r; y=CY+math.sin(a)*r
    for dx in range(-size+1,size):
        for dy in range(-size+1,size): p(c,x+dx,y+dy,col)

def branch(c,a,reach,thick,col,inner):
    x,y=CX,CY; steps=4
    for s in range(1,steps+1):
        r=reach*s/steps
        wob=math.sin(s*2.1+a*7)*0.11
        nx=CX+math.cos(a+wob)*r; ny=CY+math.sin(a+wob)*r
        c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),col,max(1,thick-(s-1)))
        c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),inner,1)
        x,y=nx,ny
        # nhanh phu
        if s>=2:
            ba=a+(0.5 if s%2 else -0.5)
            bx=x+math.cos(ba)*r*0.28; by=y+math.sin(ba)*r*0.28
            c.line(int(round(x)),int(round(y)),int(round(bx)),int(round(by)),col,max(1,thick-s))

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    reach=round(5+21*min(1,t*1.2))
    if i==0:
        c.ellipse(CX-4,CY-4,CX+4,CY+4,CRACK)
        p(c,CX,CY,HOT)
        return c
    # hoa vach: 8 nhanh chinh + 8 nhanh phu lech goc
    for k in range(8):
        branch(c,k*math.pi/4,reach,4,CRACK,ROCK)
    for k in range(8):
        branch(c,k*math.pi/4+math.pi/8,round(reach*0.72),3,ROCK_D,DUST)
    cr=max(2,round(5*(1-t*0.5)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,CRACK)
    c.ellipse(CX-cr+2,CY-cr+2,CX+cr-2,CY+cr-2,HOT if i<5 else ROCK)
    if i<5: p(c,CX,CY,GLOW)
    for k in range(12):
        dot(c,k*math.pi/6+i*0.2,reach+2+k%3,DUST)
    if i>=5:
        for k in range(8): dot(c,k*math.pi/4,round(reach*0.8),ROCK_L)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
