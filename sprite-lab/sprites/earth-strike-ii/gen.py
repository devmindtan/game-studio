#!/usr/bin/env python3
"""Earth Strike II — Fault Spikes: hai cọc đá mọc lệch nhau từ vết nứt.

DNA ĐẤT: bất đối xứng, nặng, mặt phẳng + vân, bụi, magma lộ ở khe.
Silhouette khác III (dãy 4 cọc), IV (cọc nghiêng + bụi kéo) và V (quạt + cột magma).
So sánh với frost-nova-ii: frost là vòng tuyết đối xứng, ở đây là 2 cọc đứng lệch.
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
BASE=CY+8  # chân cọc ngay dưới neo (neo = điểm cast trong game)

ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"; STRATA="#6e503c"
CRACK="#2b2028"; SHADOW="#1e161c"; DUST="#c9a882"; SAND="#a9815c"
MAGMA="#ff6a2a"; MAGMA_D="#b8331a"; GLOW="#ffd08a"; ASH="#6b5a52"
# bụi/mảnh văng mờ hơn ngưỡng hitbox (alpha 96) để hitbox chỉ đo thân cọc
F_DUST="#c9a88250"; F_ASH="#6b5a5250"; F_CHIP="#c79a6a50"

def make_rows(h,w):
    """Mỗi hàng là một đoạn liền (từ dưới lên rộng dần), tâm cố định."""
    out=[]
    for j in range(h):
        fw=max(1,min(w,int(round(w*(j+1)/h))))
        pad=(w-fw)//2
        out.append("."*pad+"#"*fw+"."*(w-fw-pad))
    return out

TALL=make_rows(26,11)
SHORT=make_rows(14,7)

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
    for k in range(3,h-2,5):
        sh=round(lean*(h-2-k)/max(1,h-1))
        line(c,cx-w//2+2+sh,base-h+1+k,cx+w//2-3+sh,base-h+1+k,STRATA)
    line(c,cx+w//2-2+lean,base-h+3,cx+w//2-2,base-1,SHADOW)
    line(c,cx-1,base-h+1,cx-1,base-3,ROCK_L)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    rise=round(11*(1-min(1,t*1.3)))
    line(c,CX-16,BASE+1,CX+15,BASE+1,CRACK,3)
    if i>=2:
        line(c,CX-6,BASE+1,CX+6,BASE+1,MAGMA_D,2)
        if i<6: line(c,CX-3,BASE+1,CX+4,BASE+1,MAGMA if i<5 else GLOW)
    spike(c,TALL,CX-7,BASE+rise,lean=0)
    spike(c,SHORT,CX+9,BASE+round(rise*0.8),lean=-2)
    for k in range(12):
        a=k*0.56+i*0.18
        p(c,CX+math.cos(a)*(6+k%6),BASE-1+math.sin(a)*2,F_DUST if k%2 else F_ASH)
    if i>=4:
        for dx,dy in [(-18,-16),(16,-20),(13,-9),(-15,-8)]:
            p(c,CX+dx,BASE+dy,F_CHIP)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(BASE-6)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
