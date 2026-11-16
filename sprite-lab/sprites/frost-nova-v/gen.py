#!/usr/bin/env python3
"""Winter's End V — chiêu tận cùng: cánh tuyết 6 nhánh, lưỡi băng quay, lõi sáng, bão tuyết."""
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

def snowflake_arm(c,a,length,width):
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    # truc chinh
    c.line(CX,CY,CX+ux*length,CY+uy*length,ICE_M,max(2,width))
    c.line(CX,CY,CX+ux*length,CY+uy*length,CORE)
    # nhanh phi 3 cap
    for s in (0.35,0.58,0.78):
        bx=CX+ux*length*s; by=CY+uy*length*s
        bl=width*(1.15-s)
        for sign in (-1,1):
            ex=bx+vx*bl*2.4*sign+ux*bl*1.5
            ey=by+vy*bl*2.4*sign+uy*bl*1.5
            c.line(int(round(bx)),int(round(by)),int(round(ex)),int(round(ey)),ICE_D,max(1,int(bl)))
            c.line(int(round(bx)),int(round(by)),int(round(ex)),int(round(ey)),ICE)
            # nhanh con
            mx=bx+vx*bl*1.3*sign; my=by+vy*bl*1.3*sign
            c.line(int(round(mx)),int(round(my)),int(round(mx+ux*bl*1.6)),int(round(my+uy*bl*1.6)),FROST)

def blade(c,a,r,size):
    # luoi băng quay theo vong ngoai (hinh thoi nghien)
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    x=CX+ux*r; y=CY+uy*r
    poly(c,[(x+ux*size,y+uy*size),(x+vx*size*0.55,y+vy*size*0.55),
            (x-ux*size,y-uy*size),(x-vx*size*0.55,y-vy*size*0.55)],ICE_D)
    c.line(int(x+ux*size),int(y+uy*size),int(x-ux*size),int(y-uy*size),CORE)
    p(c,x+ux*size,y+uy*size,CORE)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/9.0
    if i==0:
        c.ellipse(CX-5,CY-5,CX+5,CY+5,DEEP)
        c.ellipse(CX-3,CY-3,CX+3,CY+3,CORE)
        for k in range(6): dot(c,k*math.pi/3,8,ICE)
        return c
    R=round(8+30*min(1,t*1.1))
    spin=i*0.14
    # nen bang bao phu mat dat
    for rr in range(R-6,R+8,4):
        ring(c,rr,NIGHT if rr%8 else SHADOW)
    # vong ngoai: 16 luoi băng quay
    for k in range(16):
        blade(c,spin+k*math.pi/8,R,max(2,round(4+3*t)))
    # 6 nhanh tuyet chinh
    for k in range(6):
        snowflake_arm(c,k*math.pi/3+spin*0.5,round(R*0.82),max(2,round(3+2*t)))
    # vong giua: 12 vach chay ngược chieu
    ring(c,round(R*0.52),ICE_D)
    for k in range(12):
        a=-spin*1.4+k*math.pi/6
        dot(c,a,round(R*0.52),FROST if k%2 else ICE,2)
    # loi sang nhieu lop
    cr=max(3,round(10*(1-t*0.45)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,DEEP)
    c.ellipse(CX-cr+3,CY-cr+3,CX+cr-3,CY+cr-3,ICE_M)
    c.ellipse(CX-cr+6,CY-cr+6,CX+cr-6,CY+cr-6,ICE)
    c.ellipse(CX-3,CY-3,CX+3,CY+3,CORE)
    for k in range(8):
        dot(c,k*math.pi/4+spin*2,cr+4,CORE if i<8 else FROST)
    # bao tuyet
    for k in range(26):
        a=k*2.399+spin*1.7; r=round(R*(0.45+((k%9)/14)))
        dot(c,a,r,SNOW if k%4 else FROST)
    # vung nứt tren mat dat
    if i>=4:
        for k in range(12):
            a=k*math.pi/6+0.1
            for s in (R+6,R+11):
                dot(c,a,s,DEEP)
    if i==9:
        for k in range(6):
            dot(c,k*math.pi/3+spin,round(R*0.7),ICE)
    return c

ANIM=[("burst",[frame(i) for i in range(10)],11,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[3,8]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
