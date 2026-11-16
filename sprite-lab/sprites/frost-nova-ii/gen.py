#!/usr/bin/env python3
"""Frost Bloom II — hoa băng nở từ mặt đất, cánh hoa đa góc."""
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

def petal(c,a,length,width,col_mid,col_edge,col_core):
    # canh hoa: thân hẹt, đầu nhọn, có gờ sáng
    ux,uy=math.cos(a),math.sin(a)
    vx,vy=-uy,ux
    base=5
    tip=(CX+ux*length,CY+uy*length)
    l=(CX+ux*(base+length*0.45)+vx*width,CY+uy*(base+length*0.45)+vy*width)
    r=(CX+ux*(base+length*0.45)-vx*width,CY+uy*(base+length*0.45)-vy*width)
    poly(c,[l,tip,r],col_mid)
    c.line(int(l[0]),int(l[1]),int(tip[0]),int(tip[1]),col_core)
    c.line(int(tip[0]),int(tip[1]),int(r[0]),int(r[1]),col_edge)
    # gân giữa
    c.line(CX+int(ux*base),CY+int(uy*base),int(tip[0]),int(tip[1]),col_core)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-4,CY-4,CX+4,CY+4,ICE_D)
        c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE)
        return c
    # mat bang gia da dong bang
    fr=round(8+17*min(1,t*1.3))
    c.ellipse(CX-fr,CY-fr+3,CX+fr,CY+fr+6,SHADOW)
    c.ellipse(CX-fr+2,CY-fr+4,CX+fr-2,CY+fr+3,NIGHT)
    for k in range(16):
        a=k*math.pi/8
        dot(c,a,fr-2,DEEP)
    # 8 canh hoa mo dan
    length=round(6+15*min(1,t*1.15))
    width=max(2,round(3+3*min(1,t*1.4)))
    for k in range(8):
        a=k*math.pi/4 + (0.05 if i%2 else -0.05)
        petal(c,a,length,width,ICE_D,DEEP,ICE_M)
    if i>=3:
        for k in range(8):
            a=k*math.pi/4+math.pi/8
            petal(c,a,round(length*0.62),max(1,width-1),ICE,ICE_D,ICE_M)
    # nhuy hoa
    cr=max(2,round(5*(1-t*0.5)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,ICE)
    c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE if i<6 else FROST)
    # tuyet roi
    for k in range(6):
        a=k*1.7+i*0.3
        dot(c,a,fr-4+k%3,SNOW)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
