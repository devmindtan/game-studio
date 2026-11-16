#!/usr/bin/env python3
"""Tectonic Uplift III — khối đất lớn nhô lệch trái, mặt phẳng + vân + bóng.

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
SIZE=64; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))

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

# III: một khối đất khổng lồ nhô lên lệch sang trái, có mặt phẳng + vân + bóng.
def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    rise=round(2+15*min(1,t*1.15))
    # bóng trên mặt đất (lệch phải)
    poly(c,[(CX-16+4,CY+8+4),(CX+6+4,CY+10+4),(CX+12+4,CY-2+4),(CX-8+4,CY-6+4)],SHADOW)
    # thân khối
    top_y=CY-6-rise
    poly(c,[(CX-17,CY+8),(CX+7,CY+10),(CX+12,CY-2),(CX-8,top_y),(CX-20,top_y+5)],ROCK_D)
    # mặt trên nghiêng
    poly(c,[(CX-20,top_y+5),(CX-8,top_y),(CX+12,CY-2),(CX-2,CY+2)],ROCK_L)
    # vân lớp
    for k in range(3):
        yy=CY+2+k*3-rise*0.25
        line(c,CX-14,yy,CX+6,yy+1,STRATA)
    line(c,CX-20,top_y+5,CX-8,top_y,GLOW)
    line(c,CX-8,top_y,CX+12,CY-2,SAND)
    # magma lộ ở khe dưới khối
    if i>=2:
        line(c,CX+6,CY+8,CX+12,CY-2,MAGMA_D,3)
        line(c,CX+8,CY+5,CX+11,CY,MAGMA if i<6 else ASH)
    # đá rơi lộn xộn
    for k,(dx,dy,s) in enumerate([(-22,-9,2),(16,-12,3),(19,6,2),(-18,10,2),(4,-18,2)]):
        chip(c,CX+dx,CY+dy-round(rise*(0.3+k*0.1)),s)
    # bụi
    for k in range(8):
        a=k*0.78+i*0.2
        p(c,CX+math.cos(a)*(12+k%4),CY+7+math.sin(a)*4,DUST if k%2 else ASH)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
