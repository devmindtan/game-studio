#!/usr/bin/env python3
"""Seismic Vortex IV — sóng chấn động xoáy 2 chiều, lõi magma."""
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

def quake_spiral(c,phase,turn,r0,r1,thick,col_main,col_edge):
    prev=None
    steps=26
    for s in range(steps):
        u=s/(steps-1)
        r=r0+(r1-r0)*u
        a=phase+turn*u*2.5
        x=CX+math.cos(a)*r; y=CY+math.sin(a)*r
        w=max(1,round(thick*(1-u*0.7)))
        if prev:
            c.line(int(prev[0]),int(prev[1]),int(round(x)),int(round(y)),col_main,w)
            c.line(int(prev[0]),int(prev[1]),int(round(x)),int(round(y)),col_edge,1)
        for dx in range(-w+1,w): p(c,x+dx,y,col_edge)
        prev=(x,y)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-5,CY-5,CX+5,CY+5,CRACK)
        c.ellipse(CX-3,CY-3,CX+3,CY+3,HOT)
        p(c,CX,CY,GLOW)
        return c
    R=round(8+24*min(1,t*1.15))
    for rr in range(4,R+4,5):
        ring(c,rr,SMOKE if rr%10 else CRACK)
    phase=i*0.33
    for k in range(4):
        quake_spiral(c,phase+k*math.pi/2,1,4,R,4,CRACK,ROCK)
    for k in range(3):
        quake_spiral(c,phase+0.5+k*2*math.pi/3,-1,3,round(R*0.78),3,ROCK_D,DUST)
    quake_spiral(c,-phase*1.6,1,2,round(R*0.45),5,HOT,GLOW)
    cr=max(2,round(6*(1-t*0.35)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,CRACK)
    c.ellipse(CX-cr+2,CY-cr+2,CX+cr-2,CY+cr-2,MAGMA_D)
    c.ellipse(CX-2,CY-2,CX+2,CY+2,MAGMA)
    p(c,CX,CY,GLOW if i<6 else MAGMA)
    for k in range(16):
        a=phase*1.4+k*2.0; r=round(R*(0.35+((k%7)/12)))
        dot(c,a,r,DUST if k%3 else SAND)
    if i>=5:
        ring(c,R+2,ROCK_D)
        for k in range(8): dot(c,phase+k*math.pi/4+0.6,R+2,DUST)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],12,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
