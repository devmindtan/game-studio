#!/usr/bin/env python3
"""Chấn động nứt đất: vết nứt giagged mở rộng, mảnh đá văng ra rồi rơi lại, bụi bay; hitbox circle."""
import math, sys
from pathlib import Path

def _workspace():
    for parent in Path(__file__).resolve().parents:
        if (parent/"tools/gamekit/pipeline/spritekit.py").exists(): return parent
    raise SystemExit("workspace not found")
sys.path.insert(0, str(_workspace()/"tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"lib"))
from spritekit import Canvas
from sheet import export

NAME=Path(__file__).parent.name
SIZE=64; CX=CY=32; ANCHOR=(32.0,32.0); HERE=Path(__file__).parent

# Nứt đất: vết nứt giagged mở rộng, mảnh đá văng ra rồi rơi lại, bụi bay.
DARK="#2b2028"; CRACK="#5a3a34"; HOT="#d98a4a"; GLOW="#ffd08a"; DUST="#c9a882"
ROCK="#8a6a52"; ROCK_L="#c79a6a"; ROCK_D="#5a4335"

# Các nhánh nứt: mỗi nhánh là chuỗi điểm (dx,dy) tính theo tầm reach (0..1).
BRANCH=[
 [(0,0),(0.3,-0.2),(0.6,-0.1),(0.9,-0.35),(1.0,-0.2)],
 [(0,0),(0.35,0.15),(0.7,0.1),(1.0,0.35)],
 [(0,0),(-0.3,0.25),(-0.6,0.15),(-1.0,0.4)],
 [(0,0),(-0.25,-0.3),(-0.55,-0.2),(-0.9,-0.5)],
 [(0,0),(0.2,0.4),(0.45,0.6),(0.7,0.95)],
 [(0,0),(-0.2,-0.45),(-0.4,-0.7),(-0.6,-1.0)],
 [(0,0),(0.5,0.45),(0.8,0.7)],
 [(0,0),(-0.5,0.5),(-0.75,0.8)],
]

def crack(c, reach, i):
    for bi,pts in enumerate(BRANCH):
        seg=[(round(CX+dx*reach),round(CY+dy*reach)) for dx,dy in pts]
        for (x1,y1),(x2,y2) in zip(seg,seg[1:]):
            c.line(x1,y1,x2,y2,DARK,3)
            c.line(x1,y1,x2,y2,CRACK,2)
            if i in (1,2,3):
                c.line(x1,y1,x2,y2,HOT if i!=3 else GLOW,1)

def rock(c,x,y,s,hi=True):
    c.polygon([(x,y-s),(x+s,y),(x,y+s),(x-s,y)],ROCK)
    c.polygon([(x,y-s),(x+s,y),(x,y),(x-s,y)],ROCK_L if hi else ROCK_D)
    if hi: c.pixel(x-1,y-1,GLOW)

def frame(i):
    c=Canvas(SIZE,SIZE)
    reach=[3,10,15,21,20,15][i]
    if i==0:
        c.ellipse(CX-4,CY-3,CX+4,CY+3,DARK)
        c.pixel(CX,CY,HOT)
        for a in (0,90,180,270):
            x=round(CX+8*math.cos(math.radians(a))); y=round(CY+7*math.sin(math.radians(a)))
            c.pixel(x,y,DUST)
        return c
    crack(c,reach,i)
    # tâm hố
    c.ellipse(CX-3,CY-2,CX+3,CY+2,DARK)
    c.ellipse(CX-2,CY-1,CX+2,CY+1,HOT if i<4 else CRACK)
    if i in (2,3,4):
        c.pixel(CX,CY,GLOW)
    # mảnh đá văng ra theo nhánh, sau đó rơi xuống/đậu lại
    rocks=[(18,-10,3),(25,6,2),(-20,12,3),(-24,-8,2),(9,20,2),(-7,-21,3),(28,-3,2),(-28,3,2)]
    for k,(dx,dy,s) in enumerate(rocks):
        if i==2 and k>=6: continue
        t=reach/21.0
        if i==4:
            x=CX+round(dx*t*1.1); y=CY+round(dy*t*0.7)+3
            rock(c,x,y,s,hi=False)
        elif i==5:
            x=CX+round(dx*0.7); y=CY+round(dy*0.5)+4
            c.pixel(x,y,ROCK_D)
        else:
            x=CX+round(dx*t); y=CY+round(dy*t)
            rock(c,x,y,s)
            if i==3:
                c.line(x,y,x-round(dx*0.25),y-round(dy*0.25),DUST,1)
    # bụi bay
    for a in range(0,360,40):
        x=round(CX+(reach+4)*math.cos(math.radians(a)))
        y=round(CY+(reach+3)*math.sin(math.radians(a)))
        c.pixel(x,y,DUST if (i+a)%2 else ROCK_L)
    return c

ANIM=[("spell", [frame(i) for i in range(6)], 12, False,
       {"hitbox":{"shape":"circle","center":[32.0,32.0],"active":[1,4]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print(f"OK {NAME}")
