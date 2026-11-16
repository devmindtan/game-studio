#!/usr/bin/env python3
"""Worldbreaker V — chiêu tận cùng: 12 cột đá, vòng rune magma quay ngược, lõi 3 lớp và bão tro bụi."""
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
SIZE=88; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
TIER=5

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

def pillar(c,a,dist,h,w):
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    bx=CX+ux*dist; by=CY+uy*dist
    tip=(bx+uy*h*0.08,by-ux*h*0.08-h)
    l=(bx+vx*w,by+vy*w); r=(bx-vx*w,by-vy*w)
    mid=(bx+vx*w*0.45,by+vy*w*0.45-h*0.52)
    poly(c,[(l[0]+3,l[1]+4),(r[0]+3,r[1]+4),(mid[0]+3,mid[1]+3)],SMOKE)
    poly(c,[l,r,mid],ROCK_D)
    poly(c,[l,mid,tip],ROCK_L)
    poly(c,[mid,tip,r],ROCK)
    c.line(int(l[0]),int(l[1]),int(mid[0]),int(mid[1]),GLOW)
    c.line(int(mid[0]),int(mid[1]),int(tip[0]),int(tip[1]),MAGMA)
    p(c,tip[0],tip[1],GLOW)

def rune_spoke(c,a,r,size):
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    x=CX+ux*r; y=CY+uy*r
    # hinh thoi + vach ngang = rune bang
    poly(c,[(x+ux*size,y+uy*size),(x+vx*size*0.6,y+vy*size*0.6),
            (x-ux*size,y-uy*size),(x-vx*size*0.6,y-vy*size*0.6)],MAGMA_D)
    c.line(int(x+ux*size),int(y+uy*size),int(x-ux*size),int(y-uy*size),GLOW)
    c.line(int(x+vx*size*0.5),int(y+vy*size*0.5),
           int(x-vx*size*0.5),int(y-vy*size*0.5),MAGMA)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/9.0
    if i==0:
        c.ellipse(CX-6,CY-6,CX+6,CY+6,CRACK)
        c.ellipse(CX-4,CY-4,CX+4,CY+4,MAGMA_D)
        p(c,CX,CY,GLOW)
        for k in range(6): dot(c,k*math.pi/3,9,ROCK_L)
        return c
    R=round(10+30*min(1,t*1.1))
    spin=i*0.13
    # mat dat bong toa
    for rr in range(R-8,R+10,5):
        ring(c,rr,SMOKE if rr%10 else CRACK)
    # 12 cot da khong lo (khong quay) - cau truc co dinh
    for k in range(12):
        pillar(c,k*math.pi/6,R*0.78,round(8+12*t),max(2,round(3+2*t)))
    # vong rune magma quay nguoc chieu kim dong ho
    ring(c,round(R*0.55),MAGMA_D)
    for k in range(12):
        rune_spoke(c,-spin*1.3+k*math.pi/6,round(R*0.55),max(2,round(3+2*t)))
    # 8 vach overland quay thuan
    ring(c,R+4,ROCK_D)
    for k in range(8):
        dot(c,spin+k*math.pi/4,R+4,SAND if k%2 else GLOW,2)
    # loi: 3 lop magma + day nứt
    cr=max(3,round(11*(1-t*0.45)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,CRACK)
    c.ellipse(CX-cr+3,CY-cr+3,CX+cr-3,CY+cr-3,MAGMA_D)
    c.ellipse(CX-cr+6,CY-cr+6,CX+cr-6,CY+cr-6,MAGMA)
    c.ellipse(CX-3,CY-3,CX+3,CY+3,GLOW)
    for k in range(12):
        dot(c,k*math.pi/6+spin*0.5,cr+5,MAGMA if i<8 else ROCK_L)
    # tro bay (khong tuyet - day la la/dia nguc)
    for k in range(30):
        a=k*2.399+spin*1.6; r=round(R*(0.4+((k%9)/14)))
        dot(c,a,r,DUST if k%4 else SAND)
    if i==9:
        for k in range(8): dot(c,k*math.pi/4+spin,round(R*0.7),GLOW)
    return c

ANIM=[("burst",[frame(i) for i in range(10)],11,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[3,8]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
