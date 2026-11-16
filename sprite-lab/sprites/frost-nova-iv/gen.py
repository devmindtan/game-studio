#!/usr/bin/env python3
"""Blizzard Vortex IV — xoáy bão tuyết, chuyển động xoắn ốc."""
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
NIGHT="#122a52"; FROST="#9fe8ff"; SNOW="#eaf9ff"; SHADOW="#0e1c38"

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
        for dy in range(-size+1,size):
            p(c,x+dx,y+dy,col)

def spiral(c,phase,turn,r0,r1,thick,col_main,col_edge):
    prev=None
    steps=26
    for s in range(steps):
        u=s/(steps-1)
        r=r0+(r1-r0)*u
        a=phase+turn*u*2.6
        x=CX+math.cos(a)*r; y=CY+math.sin(a)*r
        w=max(1,round(thick*(1-u*0.72)))
        if prev:
            c.line(int(prev[0]),int(prev[1]),int(round(x)),int(round(y)),col_main,w)
            c.line(int(prev[0]),int(prev[1]),int(round(x)),int(round(y)),col_edge,1)
        for dx in range(-w+1,w):
            p(c,x+dx,y,w if False else col_edge)
        prev=(x,y)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-5,CY-5,CX+5,CY+5,ICE_D)
        c.ellipse(CX-3,CY-3,CX+3,CY+3,CORE)
        for k in range(4): dot(c,k*math.pi/2,7,ICE)
        return c
    R=round(7+23*min(1,t*1.15))
    # dia xoay nen
    for rr in range(4,R+4,5):
        ring(c,rr,NIGHT if rr%10 else SHADOW)
    phase=i*0.34
    # 4 nhanh xoay cung chieu kim dong ho, 3 nhanh nguoc lai
    for k in range(4):
        spiral(c,phase+k*math.pi/2,1,4,R,4,ICE_D,ICE_M)
    for k in range(3):
        spiral(c,phase+0.5+k*2*math.pi/3,-1,3,round(R*0.78),3,DEEP,FROST)
    # mat trong xoay nhanh hon
    spiral(c,-phase*1.6,1,2,round(R*0.45),5,ICE,CORE)
    # con mat ba nhanh
    cr=max(2,round(6*(1-t*0.35)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,DEEP)
    c.ellipse(CX-cr+2,CY-cr+2,CX+cr-2,CY+cr-2,ICE_M)
    c.ellipse(CX-2,CY-2,CX+2,CY+2,ICE)
    p(c,CX,CY,CORE if i<6 else FROST)
    # hat tuyet kéo theo huong xoay
    for k in range(18):
        a=phase*1.5+k*1.9; r=round(R*(0.35+((k%7)/12)))
        dot(c,a,r,SNOW if k%3 else FROST)
    if i>=5:
        ring(c,R+2,ICE_D)
        for k in range(8):
            dot(c,phase+k*math.pi/4+0.6,R+2,FROST)
    return c
ANIM=[("burst",[frame(i) for i in range(8)],12,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
