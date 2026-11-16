#!/usr/bin/env python3
"""Worldbreaker V — vực nứt chéo xuyên màn, hai mảng kiến tạo, mưa đá, tro.

DNA: ĐẤT — đứt gãy lệch trục, dịch chuyển khối, nặng, bụi, magma lộ ra.
Không dùng cấu trúc đối xứng tròn/kết tinh của dòng băng.
"""
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

ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"; STRATA="#6e503c"
CRACK="#2b2028"; SHADOW="#1e161c"; DUST="#c9a882"; SAND="#a9815c"
MAGMA="#ff6a2a"; MAGMA_D="#b8331a"; GLOW="#ffd08a"; ASH="#6b5a52"

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def poly(c,pts,col):
    c.polygon([(int(round(a)),int(round(b))) for a,b in pts],col)

def line(c,x1,y1,x2,y2,col,w=1):
    c.line(int(round(x1)),int(round(y1)),int(round(x2)),int(round(y2)),col,w)

def chip(c,x,y,s,hi=True):
    poly(c,[(x,y-s),(x+s,y),(x,y+s),(x-s,y)],ROCK if hi else ROCK_D)
    poly(c,[(x,y-s),(x+s,y),(x,y),(x-s,y)],ROCK_L if hi else SHADOW)
    p(c,x,y,GLOW if hi else STRATA)

def dust(c,x,y,r,col):
    for k in range(6):
        a=k*math.pi/3
        p(c,x+math.cos(a)*r,y+math.sin(a)*r,col)

# V: WORLDBREAKER — vực nứt chéo xuyên màn hình, hai mảng kiến tạo nghiêng, magma tràn, mưa đá, tro.
EDGE_A=[(-38,-30),(-30,-24),(-23,-27),(-14,-17),(-6,-19),(3,-9),(12,-11),(21,-1),(30,2),(38,12)]
EDGE_B=[(-36,-24),(-28,-18),(-21,-21),(-12,-11),(-4,-13),(5,-3),(14,-5),(23,5),(32,8),(38,17)]

def edge(c,pts,col,w=1):
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        line(c,CX+x1,CY+y1,CX+x2,CY+y2,col,w)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/9.0
    grow=min(1,t*1.2)
    if i==0:
        c.ellipse(CX-7,CY-5,CX+7,CY+5,CRACK)
        c.ellipse(CX-4,CY-3,CX+4,CY+3,MAGMA_D)
        c.pixel(CX,CY,GLOW)
        return c
    n=max(2,int(len(EDGE_A)*grow))
    a=EDGE_A[:n]; b=EDGE_B[:n]
    # vực: lấp giữa hai bờ bằng nền tối rồi magma
    for (x1,y1),(x2,y2) in zip(a,b):
        c.polygon([(int(CX+x1),int(CY+y1)),(int(CX+x2),int(CY+y2)),
                   (int(CX+x2+4),int(CY+y2+4)),(int(CX+x1+4),int(CY+y1+4))],CRACK)
    # magma trong vực
    for (x1,y1),(x2,y2) in zip(a,b):
        line(c,CX+(x1+x2)/2,CY+(y1+y2)/2,CX+(x1+x2)/2+3,CY+(y1+y2)/2+3,
             MAGMA_D if i<8 else ASH, 5)
        if i<8: line(c,CX+(x1+x2)/2,CY+(y1+y2)/2,CX+(x1+x2)/2+3,CY+(y1+y2)/2+3,MAGMA,2)
    # hai bờ đá có vân (bất đối xứng: bờ trên dày hơn)
    edge(c,a,SHADOW,6); edge(c,b,ROCK_D,4)
    edge(c,a,ROCK_L,2); edge(c,b,STRATA,1)
    for k,(x,y) in enumerate(a[1:],start=1):
        if k%2==0:
            chip(c,CX+x-4,CY+y-4,3,k%3==0)
            chip(c,CX+x+3,CY+y+4,2)
    # mảng kiến tạo nghiêng ở hai đầu (không đối xứng)
    poly(c,[(CX-38,CY-30),(CX-18,CY-42),(CX+2,CY-30),(CX-23,CY-27)],ROCK_D)
    poly(c,[(CX-38,CY-30),(CX-18,CY-42),(CX-23,CY-27)],ROCK_L)
    poly(c,[(CX+18,CY+9),(CX+38,CY+12),(CX+30,CY+28),(CX+12,CY+22)],ROCK_D)
    poly(c,[(CX+18,CY+9),(CX+38,CY+12),(CX+30,CY+28)],ROCK)
    for k in range(3):
        line(c,CX-33,CY-30+k*3,CX-20,CY-34+k*2,STRATA)
        line(c,CX+17,CY+13+k*3,CX+32,CY+17+k*2,STRATA)
    # mưa đá rơi xuống vực
    for k in range(12):
        x=CX-34+k*6+(k%3)*2
        y=CY-24+((k*7+i*5)%26)
        if (x-CX) > (y-CY)*0.8 - 22:
            chip(c,x,y,2 if k%3==0 else 1,hi=(k+i)%2==0)
    # tro/bụi bay
    for k in range(30):
        ang=k*2.399+i*0.09
        r=18+(k%11)*2
        p(c,CX+math.cos(ang)*r,CY+math.sin(ang)*r*0.7,DUST if k%4 else ASH)
    if i==9:
        for k in range(8): p(c,CX+4+k*4,CY+4+k*3,GLOW if k%2 else MAGMA)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],11,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
