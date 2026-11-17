#!/usr/bin/env python3
"""Frost Nova IV — ngôi sao + mảnh băng của bậc III (giữ nguyên), nay các mảnh xoáy quanh ngôi sao theo đường xoắn ốc, để lại vệt tuyết.

DNA băng: kết tinh, đối xứng tròn, cạnh sắc. Kế thừa: III = ngôi sao + mảnh bắn ra; IV = + mảnh xoáy quanh (vệt tuyết).
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
TIER=4

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

def shard(c,a,dist,ln,w):
    # manh bang hinh thoi nhon theo huong bay
    ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    bx,by=CX+ux*dist,CY+uy*dist
    tip=(bx+ux*ln,by+uy*ln); tail=(bx-ux*ln*0.5,by-uy*ln*0.5)
    l=(bx+vx*w,by+vy*w); r=(bx-vx*w,by-vy*w)
    poly(c,[tail,l,tip,r],ICE_M)
    c.line(int(round(tail[0])),int(round(tail[1])),int(round(tip[0])),int(round(tip[1])),ICE)
    p(c,tip[0],tip[1],CORE)

def shard_at(c,pos_a,dist,dir_a,ln,w):
    # manh bang dat o goc pos_a, mui nghieng theo huong xoay dir_a
    bx,by=CX+math.cos(pos_a)*dist,CY+math.sin(pos_a)*dist
    ux,uy=math.cos(dir_a),math.sin(dir_a); vx,vy=-uy,ux
    tip=(bx+ux*ln*0.6,by+uy*ln*0.6); tail=(bx-ux*ln*0.6,by-uy*ln*0.6)
    l=(bx+vx*w,by+vy*w); r=(bx-vx*w,by-vy*w)
    poly(c,[tail,l,tip,r],ICE_M)
    c.line(int(round(tail[0])),int(round(tail[1])),int(round(tip[0])),int(round(tip[1])),ICE)
    p(c,tip[0],tip[1],CORE)

def frame(i):
    c=Canvas(SIZE,SIZE)
    t=i/7.0
    if i==0:
        c.ellipse(CX-4,CY-4,CX+4,CY+4,ICE_D)
        c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE)
        return c
    # chi ngoi sao bang: khong ve nen tron toi ben duoi (nguoi dung 2026-11-17)
    # 8 canh hoa mo dan
    length=round(8+18*min(1,t*1.15))
    width=max(2,round(3+3*min(1,t*1.4)))
    for k in range(8):
        a=k*math.pi/4 + (0.05 if i%2 else -0.05)
        petal(c,a,length,width,ICE_D,DEEP,ICE_M)
    if i>=3:
        for k in range(8):
            a=k*math.pi/4+math.pi/8
            petal(c,a,round(length*0.62),max(1,width-1),ICE,ICE_D,ICE_M)
    # moi: manh bang bay ra tu dau moi canh lon (tu frame 4)
    if i>=4:
        d=min(length+3+(i-4)*2, CX-9)   # tip stays inside the frame, 2 px margin
        spin=(i-4)*0.24                 # moi: manh xoay quanh ngoi sao
        for k in range(8):
            a=k*math.pi/4+spin
            # vet tuyet phia sau theo cung tron
            for j in range(1,9):
                col=FROST if j<=2 else (ICE_D if j<=5 else DEEP)
                dot(c,a-0.07*j,d,col)
            shard_at(c,a,d,a+math.pi/2,7,2)
    # nhuy hoa
    cr=max(2,round(5*(1-t*0.5)))
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,ICE)
    c.ellipse(CX-2,CY-2,CX+2,CY+2,CORE if i<6 else FROST)
    return c

ANIM=[("burst",[frame(i) for i in range(8)],13,False,
       {"hitbox":{"shape":"circle","center":[float(CX),float(CY)],"active":[2,6]}})]
if __name__=="__main__":
    export(HERE,NAME,ANIM,anchor=ANCHOR)
    print("OK",NAME)
