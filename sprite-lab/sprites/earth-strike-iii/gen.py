#!/usr/bin/env python3
"""Earth Strike III — Spike Ridge: hàng cọc đá cao thấp dọc theo vết nứt.

DNA ĐẤT: bất đối xứng, khối đặc có mặt phẳng/vân, bụi dày, magma trong khe.
Silhouette = dãy răng cưa ngang (khác II: 2 cọc; khác IV: cọc nghiêng; khác V: quạt + cột).
So sánh frost-nova-iii: một cột băng kết tinh, ở đây là 4 cọc rời nhau.
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

ROWS={18:make_rows(18,7), 24:make_rows(24,9), 30:make_rows(30,11)}
SPIKES=[(-21,18),(-8,30),(7,24),(20,18)]

def p(c,x,y,col):
    xi,yi=int(round(x)),int(round(y))
    if 0<=xi<SIZE and 0<=yi<SIZE: c.pixel(xi,yi,col)

def line(c,x1,y1,x2,y2,col,w=1):
    c.line(int(round(x1)),int(round(y1)),int(round(x2)),int(round(y2)),col,w)

def spike(c,rows,cx,base):
    h=len(rows); w=len(rows[0])
    for j,row in enumerate(rows):
        y=base-h+1+j
        for i,ch in enumerate(row):
            if ch!='#': continue
            col=ROCK_L if i<w//2 and j<h-3 else (ROCK_D if j>=h-3 else ROCK)
            p(c,cx-w//2+i,y,col)
    for k in range(4,h-2,6):
        line(c,cx-w//2+2,base-h+1+k,cx+w//2-3,base-h+1+k,STRATA)
    line(c,cx+w//2-2,base-h+3,cx+w//2-2,base-1,SHADOW)
    line(c,cx-1,base-h+1,cx-1,base-2,ROCK_L)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    line(c,CX-27,BASE+1,CX+26,BASE+1,CRACK,3)
    if i>=2:
        line(c,CX-17,BASE+1,CX+19,BASE+1,MAGMA_D,2)
        if i<6: line(c,CX-9,BASE+1,CX+12,BASE+1,MAGMA if i<5 else GLOW)
    for k,(dx,h) in enumerate(SPIKES):
        delay=k*0.06
        rise=round(12*(1-min(1,max(0,(t-delay)*1.35))))
        spike(c,ROWS[h],CX+dx,BASE+rise)
    for k in range(24):
        a=k*0.29+i*0.12
        p(c,CX+math.cos(a)*(7+k%9),BASE-1+math.sin(a)*3,F_DUST if k%3 else F_ASH)
    if i>=3:
        for dx,dy in [(-25,-24),(24,-27),(-3,-32),(15,-31)]:
            p(c,CX+dx,BASE+dy,F_CHIP)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(BASE-8)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
