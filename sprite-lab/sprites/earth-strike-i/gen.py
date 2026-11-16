#!/usr/bin/env python3
"""Earth Strike I — vết nứt đất cơ bản, đá văng nhẹ."""
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

def bolt(c,a,reach,seed):
    x,y=CX,CY
    for s in range(1,5):
        r=reach*s/4
        wob=math.sin(s*2.3+seed)*0.09
        nx=CX+math.cos(a+wob)*r; ny=CY+math.sin(a+wob)*r
        c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),CRACK,max(1,4-s))
        if s>=3: c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),ROCK,1)
        x,y=nx,ny

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    reach=round(3+17*min(1,t*1.2))
    if i==0:
        c.ellipse(CX-4,CY-3,CX+4,CY+3,CRACK)
        c.pixel(CX,CY,HOT)
        return c
    for k in range(6):
        bolt(c,k*math.pi/3+0.1,reach,k*1.7+i*0.2)
    c.ellipse(CX-4,CY-3,CX+4,CY+3,CRACK)
    c.ellipse(CX-2,CY-2,CX+2,CY+2,HOT if i<5 else ROCK)
    if i<5: p(c,CX,CY,GLOW)
    for k in range(8):
        dot(c,k*math.pi/4+i*0.1,reach-1+k%3,DUST)
    if i==7:
        for k in range(6): dot(c,k*math.pi/3,round(reach*0.6),ROCK_D)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],14,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
