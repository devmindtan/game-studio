#!/usr/bin/env python3
"""Earth Strike IV — Sliding Ridge: cọc đá nghiêng trượt, bụi kéo dài theo hướng.

DNA ĐẤT: chuyển động của chất liệu — cọc nghiêng dần, mảnh vỡ trượt xuống,
bụi kéo dài, magma chỉ còn ở khe sau lưng.
Silhouette = cọc nghiêng + vệt bụi ngang (khác II cọc đứng, III dãy thẳng, V quạt + cột).
So sánh frost-nova-iv: xoáy tuyết tròn, ở đây là khối đá nghiêng có trọng lực.
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
SIZE=72; CX=CY=SIZE//2; ANCHOR=(float(CX),float(CY))
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

TALL=make_rows(34,11); MID=make_rows(22,9); SMALL=make_rows(13,7)

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def line(c,x1,y1,x2,y2,col,w=1):
    c.line(int(round(x1)),int(round(y1)),int(round(x2)),int(round(y2)),col,w)

def spike(c,rows,cx,base,lean):
    h=len(rows); w=len(rows[0])
    for j,row in enumerate(rows):
        y=base-h+1+j
        sh=round(lean*(h-1-j)/max(1,h-1))
        for i,ch in enumerate(row):
            if ch!='#': continue
            col=ROCK_L if i<w//2 and j<h-3 else (ROCK_D if j>=h-3 else ROCK)
            p(c,cx-w//2+i+sh,y,col)
    for k in range(4,h-2,6):
        sh=round(lean*(h-2-k)/max(1,h-1))
        line(c,cx-w//2+2+sh,base-h+1+k,cx+w//2-3+sh,base-h+1+k,STRATA)
    line(c,cx+w//2-2+lean,base-h+3,cx+w//2-2,base-1,SHADOW)
    line(c,cx-1+round(lean*0.4),base-h+1,cx-1,base-2,ROCK_L)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    lean=round(7*min(1,t*1.3))
    line(c,CX-25,BASE+1,CX+28,BASE+1,CRACK,3)
    if i>=2:
        line(c,CX-15,BASE+1,CX+9,BASE+1,MAGMA_D,2)
        if i<5: line(c,CX-9,BASE+1,CX+3,BASE+1,MAGMA)
    spike(c,TALL,CX-11,BASE+round(11*(1-min(1,t*1.3))),lean)
    spike(c,MID,CX+10,BASE,max(2,lean-2))
    spike(c,SMALL,CX+25,BASE+2,max(2,lean-4))
    for k in range(30):
        u=(k%15)/14.0
        x=CX-13+lean*3+k%8+u*20
        y=BASE-1-((i+k*3)%7)
        p(c,x,y,F_DUST if k%3 else F_ASH)
    if i>=3:
        for k in range(6):
            p(c,CX+8+k*4,BASE-3-(k%4),F_CHIP)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(BASE-10)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
