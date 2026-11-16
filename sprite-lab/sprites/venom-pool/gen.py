#!/usr/bin/env python3
"""Hồ độc lan rộng rồi co lại: chất lỏng có bờ loe, bọt khí, hơi độc; hitbox circle."""
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

# Hồ độc: vùng chất lỏng có bờ loe, bọt khí nổi, hơi độc bay lên.
DARK="#173d2a"; EDGE="#2b7a4a"; MID="#3fae5c"; LIT="#7ede6a"; ACID="#c6f36a"; FOAM="#eaff9a"; VAPOR="#6fdc7a33"

# Hệ số bờ loe theo từng hàng (cố ý không đều; -1..1 nhân với bán kính).
SHAPE=[0.0,0.55,0.85,0.7,1.0,0.9,0.75,1.0,0.85,0.95,0.7,0.8,0.6,0.65,0.45,0.5,0.25]

def blob(c, rad):
    for j,f in enumerate(SHAPE):
        w=max(1,round(rad*f))
        for sy in (-1,1):
            y=CY+sy*j
            c.rect(CX-w,y,CX+w,y,DARK)
            iw=max(0,w-2)
            if iw: c.rect(CX-iw,y,CX+iw,y,EDGE)
            cw=max(0,w-5)
            if j<len(SHAPE)-4 and cw: c.rect(CX-cw,y,CX+cw,y,MID if j%2 else LIT)

BUBBLES=[(-8,-4,2),(7,-6,3),(-2,3,2),(9,4,2),(-11,2,2),(3,8,3),(-5,-9,2),(12,-1,2)]
DRIPS=[(-12,5),(11,7),(-6,11),(6,-11)]

def frame(i):
    c=Canvas(SIZE,SIZE)
    rad=[4,9,14,18,16,9][i]
    if i==0:
        c.ellipse(CX-5,CY-4,CX+5,CY+4,MID)
        c.ellipse(CX-3,CY-2,CX+3,CY+2,LIT)
        c.pixel(CX,CY,FOAM)
        for a in range(0,360,45):
            x=round(CX+11*math.cos(math.radians(a))); y=round(CY+9*math.sin(math.radians(a)))
            c.pixel(x,y,ACID)
        return c
    blob(c,rad)
    for k,(dx,dy,r) in enumerate(BUBBLES):
        if i==5 and k%2: continue
        x=CX+round(dx*rad/18); y=CY+round(dy*rad/18)
        rr=max(1,round(r*rad/18))
        c.ellipse(x-rr,y-rr,x+rr,y+rr,EDGE)
        c.ellipse(x-rr+1,y-rr+1,x+rr-1,y+rr-1,FOAM if (i+k)%2 else ACID)
        c.pixel(x-1,y-1,"#ffffff")
    for dx,dy in ((-6,-14),(2,-17),(9,-12),(-11,-10)):
        x=CX+round(dx*rad/18); y=CY+round(dy*rad/18)-(i*2 if i<4 else 4)
        c.ellipse(x-2,y-2,x+2,y+1,VAPOR)
    if i in (2,3,4):
        for dx,dy in DRIPS:
            x=CX+round(dx*rad/18); y=CY+round(dy*rad/18)
            c.pixel(x,y,ACID); c.pixel(x,y+1,LIT)
    return c

ANIM=[("spell", [frame(i) for i in range(6)], 12, False,
       {"hitbox":{"shape":"circle","center":[32.0,32.0],"active":[1,4]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print(f"OK {NAME}")
