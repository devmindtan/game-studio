#!/usr/bin/env python3
"""Earth Strike I — một vết đứt lệch, đá văng, bụi thấp.

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
SIZE=48; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))

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

# I: một vết đứt lệch, không đối xứng, vài mảnh đá bắn ra.
PATH=[(-12,9),(-6,5),(-1,7),(5,1),(12,-2),(17,-10)]

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-3,CY-1,CX+3,CY+3,CRACK)
        p(c,CX,CY,HOT if False else GLOW)
        return c
    n=max(2,int(len(PATH)*min(1,t*1.25)))
    pts=[(CX+dx,CY+dy) for dx,dy in PATH[:n]]
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        line(c,x1,y1,x2,y2,CRACK,5)
        line(c,x1,y1,x2,y2,ROCK_D,3)
        line(c,x1,y1,x2,y2,ROCK_L if i<4 else STRATA,1)
    # mảnh văng ở đầu vết nứt, lệch hẳn sang phải
    if i>=2:
        ex,ey=pts[-1]
        chip(c,ex+3,ey-3,2)
        chip(c,ex+6,ey+1,2,i>4)
        chip(c,ex-2,ey-5,1)
    # bụi thấp sát mặt đất
    for k in range(5):
        a=k*1.3+i*0.2
        r=6+k%3
        p(c,CX+math.cos(a)*r+2,CY+math.sin(a)*r+4,DUST if k%2 else SAND)
    if i==7:
        for k in range(4): p(c,CX+8+k*3,CY-6-k,ROCK_D)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],14,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
