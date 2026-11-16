#!/usr/bin/env python3
"""Tectonic Spires III — cột đá 3D mọc lên từ nền nứt nẻ."""
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
SIZE=64; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
TIER=3

# palette đất/đá
SHADOW="#1e161c"
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

def boulder(c,a,dist,h,w):
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    bx=CX+ux*dist; by=CY+uy*dist
    tip=(bx+uy*h*0.1,by-ux*h*0.1-h)
    l=(bx+vx*w,by+vy*w)
    r=(bx-vx*w,by-vy*w)
    mid=(bx+vx*w*0.5,by+vy*w*0.5-h*0.5)
    poly(c,[(l[0]+2,l[1]+3),(r[0]+2,r[1]+3),(mid[0]+2,mid[1]+2)],SHADOW)
    poly(c,[l,r,mid],ROCK_D)
    poly(c,[l,mid,tip],ROCK_L)
    poly(c,[mid,tip,r],ROCK)
    c.line(int(l[0]),int(l[1]),int(mid[0]),int(mid[1]),SAND)
    c.line(int(mid[0]),int(mid[1]),int(tip[0]),int(tip[1]),GLOW)
    p(c,tip[0],tip[1],ROCK_L)

def fissure(c,a,reach):
    x,y=CX,CY
    for s in range(1,5):
        r=reach*s/4
        wob=math.sin(s*2.4+a*5)*0.1
        nx=CX+math.cos(a+wob)*r; ny=CY+math.sin(a+wob)*r
        c.line(int(x),int(y),int(nx),int(ny),CRACK,max(1,5-s))
        if s>=3: c.line(int(x),int(y),int(nx),int(ny),MAGMA_D if TIER>=4 else ROCK,1)
        x,y=nx,ny

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    reach=round(6+20*min(1,t*1.2))
    if i==0:
        c.ellipse(CX-4,CY-4,CX+4,CY+4,CRACK)
        p(c,CX,CY,HOT)
        return c
    for k in range(8): fissure(c,k*math.pi/4+0.1,reach)
    h=round(4+15*min(1,t*1.15))
    w=max(2,round(3+3*min(1,t*1.5)))
    dist=round(5+9*min(1,t*1.2))
    for k in range(8):
        boulder(c,k*math.pi/4,dist,h,w)
    if i>=4:
        for k in range(8): boulder(c,k*math.pi/4+math.pi/8,dist+3,round(h*0.62),max(1,w-1))
    cr=max(2,round(5*(1-t*0.6)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,CRACK)
    c.ellipse(CX-cr+2,CY-cr+2,CX+cr-2,CY+cr-2,HOT if i<5 else ROCK)
    if i<5: p(c,CX,CY,GLOW)
    for k in range(10): dot(c,k*2.1+i*0.4,reach-2+k%4,DUST)
    if i==7:
        for k in range(8): dot(c,k*math.pi/4,round(reach*0.65),ROCK_D)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
