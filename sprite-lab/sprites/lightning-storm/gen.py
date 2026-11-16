#!/usr/bin/env python3
"""Bão sét: nhiều điểm sét giáng có chạm đất trong vùng tròn tích điện; hitbox circle."""
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

# Bão sét: vùng mây tích điện, nhiều điểm sét giáng xuống đất (có chạm đất), sáng theo nhịp.
CLOUD="#2b2350"; CLOUD_L="#4a3d86"; ARC="#7d8bff"; BOLT="#b7c4ff"; CORE="#ffffff"; CYAN="#72e8ff"

POINTS=[(22,22),(43,25),(27,43),(45,44)]
# lịch đánh theo frame: frame nào điểm nào sáng
ACTIVE={1:[0],2:[1,2],3:[0,1,2,3],4:[1,3]}

def field(c,r,i):
    c.ellipse(CX-r,CY-r,CX+r,CY+r,CLOUD,False)
    c.ellipse(CX-r+3,CY-r+3,CX+r-3,CY+r-3,CLOUD_L,False)
    # tia điện li ti trên mây
    for a in range(0,360,30):
        x=round(CX+(r-2)*math.cos(math.radians(a+i*7)))
        y=round(CY+(r-2)*math.sin(math.radians(a+i*7)))
        c.pixel(x,y,ARC if (a+i)%2 else CYAN)

def bolt(c,x,y,i):
    # đường sét zigzag từ trên xuống điểm chạm đất
    pts=[(x,7),(x-3,13),(x+2,17),(x-2,23),(x+3,28),(x-1,y-4),(x,y)]
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        c.line(x1,y1,x2,y2,ARC,3)
        c.line(x1,y1,x2,y2,BOLT,1)
        if i==3: c.line(x1,y1,x2,y2,CORE,1)
    # điểm chạm đất: ngôi sao + vòng nổ
    c.ellipse(x-5,y-3,x+5,y+3,BOLT)
    c.ellipse(x-3,y-2,x+3,y+2,CORE)
    for dx,dy in ((7,0),(-7,0),(0,4),(0,-4),(5,4),(-5,-4),(5,-4),(-5,4)):
        c.line(x,y,x+dx,y+dy,BOLT if abs(dx)+abs(dy)>7 else CORE,1)

def frame(i):
    c=Canvas(SIZE,SIZE)
    r=[10,16,21,23,21,14][i]
    field(c,r,i)
    for n,(x,y) in enumerate(POINTS):
        if n in ACTIVE.get(i,[]):
            bolt(c,x,y,i)
        elif i in (0,5):
            c.ellipse(x-2,y-2,x+2,y+2,CLOUD_L)
            c.pixel(x,y,ARC)
    if i==3:
        # chớp toàn vùng
        for a in range(0,360,45):
            x=round(CX+(r-4)*math.cos(math.radians(a))); y=round(CY+(r-4)*math.sin(math.radians(a)))
            c.pixel(x,y,CYAN)
    return c

ANIM=[("spell", [frame(i) for i in range(6)], 12, False,
       {"hitbox":{"shape":"circle","center":[32.0,32.0],"active":[1,4]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print(f"OK {NAME}")
