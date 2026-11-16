#!/usr/bin/env python3
"""Frost Nova I — vụ nổ băng nhỏ, vòng băng + mảnh băng."""
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
SIZE=48; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
TIER=1

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

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-3,CY-3,CX+3,CY+3,ICE_M)
        c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE)
        for k in range(8):
            dot(c,k*math.pi/4,5,ICE)
        return c
    r=round(4+16*t)
    ring(c,r,DEEP if i>=3 else ICE_D)
    ring(c,max(2,round(r*0.62)),ICE_M)
    cr=max(1,round(3*(1-t*0.6)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,ICE)
    p(c,CX,CY,CORE if i<6 else ICE)
    n=8 if i<3 else 12
    for k in range(n):
        a=k*2*math.pi/n + (0.09 if i%2 else -0.09)
        rad=r+(k%3)
        dot(c,a,rad,ICE if k%2 else FROST,2 if i<5 else 1)
    if i>=4:
        for k in range(4):
            dot(c,k*math.pi/2+math.pi/4,round(r*0.8),SNOW)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],14,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
