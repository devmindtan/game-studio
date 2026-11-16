#!/usr/bin/env python3
"""Worldbreaker V — Quạt cọc đá + cột magma trung tâm, mưa mảnh vụn.

DNA ĐẤT: bố cục hoàn toàn mới — quạt cọc tỏa rộng, cọc giữa cao nhất,
magma phun giữa các khe, đá rơi và tro mù. Không lặp vực nứt chéo cũ,
không lặp dãy ngang của III hay cọc nghiêng của IV.
So sánh frost-nova-v: bông tuyết đối xứng; ở đây là quạt cọc bất đối xứng có trọng lực.
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
BASE=CY+8  # chân cọc ngay dưới neo (neo = điểm cast trong game)

ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"; STRATA="#6e503c"
CRACK="#2b2028"; SHADOW="#1e161c"; DUST="#c9a882"; SAND="#a9815c"
MAGMA="#ff6a2a"; MAGMA_D="#b8331a"; GLOW="#ffd08a"; ASH="#6b5a52"
F_DUST="#c9a88250"; F_ASH="#6b5a5250"; F_CHIP="#c79a6a50"

def make_rows(h,w):
    out=[]
    for j in range(h):
        fw=max(1,min(w,int(round(w*(j+1)/h))))
        pad=(w-fw)//2
        out.append("."*pad+"#"*fw+"."*(w-fw-pad))
    return out

ROWS={16:make_rows(16,7), 24:make_rows(24,9), 42:make_rows(42,13)}
FAN=[(-36,16,-3),(-24,24,-2),(-11,42,-1),(5,42,1),(20,24,2),(33,16,3)]

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def line(c,x1,y1,x2,y2,col,w=1):
    c.line(int(round(x1)),int(round(y1)),int(round(x2)),int(round(y2)),col,w)

def spike(c,rows,cx,base,lean=0):
    h=len(rows); w=len(rows[0])
    for j,row in enumerate(rows):
        y=base-h+1+j
        sh=round(lean*(h-1-j)/max(1,h-1))
        for i,ch in enumerate(row):
            if ch!='#': continue
            col=ROCK_L if i<w//2 and j<h-3 else (ROCK_D if j>=h-3 else ROCK)
            p(c,cx-w//2+i+sh,y,col)
    for k in range(5,h-2,8):
        sh=round(lean*(h-2-k)/max(1,h-1))
        line(c,cx-w//2+2+sh,base-h+1+k,cx+w//2-3+sh,base-h+1+k,STRATA)
    line(c,cx+w//2-2+lean,base-h+3,cx+w//2-2,base-1,SHADOW)
    line(c,cx-1+round(lean*0.3),base-h+1,cx-1,base-2,ROCK_L)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/9.0
    line(c,CX-40,BASE+1,CX+40,BASE+1,CRACK,4)
    if i>=2:
        h=round(26*min(1,(t-0.1)*1.7))
        for k in range(h):
            y=BASE-k
            w=max(1,3-k//6)
            line(c,CX-w,y,CX+w,y,MAGMA_D if k>h//2 or i>7 else MAGMA)
            if k%3==0 and i<8: p(c,CX-k%3,y,GLOW)
    for k,(dx,rows,lean) in enumerate(FAN):
        delay=k*0.05
        rise=round(14*(1-min(1,max(0,(t-delay)*1.3))))
        spike(c,ROWS[rows],CX+dx,BASE+rise,lean)
    for k in range(18):
        x=CX-36+((k*11+i*7)%72)
        y=CY-38+((k*13+i*9)%52)
        p(c,x,y,F_CHIP)
    for k in range(40):
        a=k*2.399+i*0.07
        r=10+(k%13)*2
        p(c,CX+math.cos(a)*r,BASE-1+math.sin(a)*4,F_DUST if k%4 else F_ASH)
    if i==9:
        for k in range(10): p(c,CX-9+k*2,BASE-3-(k%3),GLOW if k%2 else MAGMA)
    return c

ANIM=[("burst",[frame(i) for i in range(10)],11,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(BASE-12)],"active":[3,8]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
