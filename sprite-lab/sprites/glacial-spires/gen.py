#!/usr/bin/env python3
"""Glacial Spires — chiêu riêng (tách từ Frost Nova III cũ, 2026-11-17): cọc băng mọc lên, mặt đất nứt nẻ."""
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
TIER=0   # chiêu riêng, chưa có bậc

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

def gem(c,a,dist,h,size):
    # tinh thể đứng: đáy có bóng, thân khối lăng trụ, mặt sáng/trối rõ
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    bx=CX+ux*dist; by=CY+uy*dist
    tip=(bx+uy*h*0.15, by-ux*h*0.15-h)
    base_l=(bx+vx*size,by+vy*size)
    base_r=(bx-vx*size,by-vy*size)
    mid_l=(bx+vx*size*0.55-uy*h*0.05, by+vy*size*0.55-ux*h*0.05-h*0.55)
    mid_r=(bx-vx*size*0.55-uy*h*0.05, by-vy*size*0.55-ux*h*0.05-h*0.55)
    poly(c,[(base_l[0]+2,base_l[1]+3),(base_r[0]+2,base_r[1]+3),
            (mid_r[0]+2,mid_r[1]+2),(mid_l[0]+2,mid_l[1]+2)],SHADOW)
    poly(c,[base_l,base_r,mid_r,mid_l],ICE_D)
    poly(c,[mid_l,mid_r,tip],ICE)
    poly(c,[mid_r,tip,(bx+ux*size*0.2,by+uy*size*0.2-h*0.6)],DEEP)
    c.line(int(mid_l[0]),int(mid_l[1]),int(tip[0]),int(tip[1]),ICE_M)
    c.line(int(base_l[0]),int(base_l[1]),int(mid_l[0]),int(mid_l[1]),FROST)
    p(c,tip[0],tip[1],CORE)
    # mat truoc: vach sang
    c.line(int(base_l[0]),int(base_l[1]),int(mid_l[0]),int(mid_l[1]),CORE)

def crack(c,a,reach):
    x,y=CX,CY
    for s in range(1,5):
        rr=reach*s/4
        wob=math.sin(s*2.3+a*7)*2
        nx=CX+math.cos(a+wob*0.01)*rr
        ny=CY+math.sin(a+wob*0.01)*rr
        c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),NIGHT,max(1,4-s))
        if s>2: c.line(int(round(x)),int(round(y)),int(round(nx)),int(round(ny)),ICE_D)
        x,y=nx,ny

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    reach=round(6+20*min(1,t*1.2))
    for k in range(8):
        crack(c,k*math.pi/4+0.08,reach)
    if i==0:
        c.ellipse(CX-4,CY-4,CX+4,CY+4,ICE_M)
        p(c,CX,CY,CORE)
        return c
    h=round(4+16*min(1,t*1.15))
    size=max(2,round(2+2*min(1,t*1.5)))
    dist=round(5+9*min(1,t*1.2))
    # 8 tinh the lon theo vong, 8 tinh the nho xen ke
    for k in range(8):
        gem(c,k*math.pi/4,dist,h,size)
    if i>=4:
        for k in range(8):
            gem(c,k*math.pi/4+math.pi/8,dist+3,round(h*0.6),max(1,size-1))
    cr=max(1,round(4*(1-t*0.7)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,DEEP)
    c.ellipse(CX-cr+1,CY-cr+1,CX+cr-1,CY+cr-1,ICE)
    p(c,CX,CY,CORE)
    for k in range(10):
        dot(c,k*2.1+i*0.4,reach-2+k%4,SNOW)
    if i==7:
        for k in range(8):
            dot(c,k*math.pi/4,round(reach*0.65),DEEP)
    return c
ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
