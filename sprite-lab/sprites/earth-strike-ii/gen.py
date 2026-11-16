#!/usr/bin/env python3
"""Fault Slip II — hai tảng nền trượt ngược, khe hở lộ magma.

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
SIZE=56; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))

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

# II: hai tảng nền trượt ngược nhau như đứt gãy kiểu strike-slip, bất đối xứng.
def slab(c,pts,lift,shade):
    moved=[(x,y-lift) for x,y in pts]
    shadow=[(x+3,y-lift+4) for x,y in pts]
    poly(c,shadow,SHADOW)
    poly(c,moved,shade)
    # đường vân nằm ngang trên mặt tảng
    for k in range(3):
        yy=moved[0][1]+4+k*4-lift
        line(c,moved[0][0]+2,yy,moved[2][0]-2,yy-2,STRATA)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    lift=round(2+9*min(1,t*1.2))
    left=[(CX-20,CY+4),(CX-9,CY+11),(CX-2,CY-1),(CX-12,CY-10)]
    right=[(CX+3,CY-9),(CX+19,CY+1),(CX+13,CY+12),(CX+2,CY+3)]
    slab(c,left,lift,ROCK_D)
    slab(c,right,round(lift*0.55),ROCK)
    # khe hở giữa hai tảng lộ magma
    line(c,CX-2,CY+2-lift,CX+3,CY+1-round(lift*0.55),CRACK,6)
    if i>=2:
        line(c,CX-1,CY+1-lift,CX+2,CY+1-round(lift*0.55),MAGMA_D,2)
        if i<6: line(c,CX,CY+1-lift,CX+1,CY+1-round(lift*0.55),GLOW)
    # bụi dưới chân tảng
    for k in range(7):
        a=k*0.9+i*0.15
        p(c,CX-4+math.cos(a)*(8+k%4),CY+6+math.sin(a)*3,DUST if k%2 else ASH)
    if i>=3:
        chip(c,CX-11,CY-11-lift,2)
        chip(c,CX+14,CY-8-round(lift*0.55),2,i>5)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
