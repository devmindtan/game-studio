#!/usr/bin/env python3
"""Vòng rune 8 glyph phát sáng theo hai nhịp; hitbox circle."""
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

# Vòng rune: nhiều glyph đọc được xếp quanh vòng, phát sáng theo hai nhịp.
DIM="#4a2f7a"; RING="#8450c0"; RUNE="#c47bff"; LIT="#f0c8ff"; WHITE="#ffffff"; CYAN="#7ce8ff"

# 8 glyph 5x5 (mỗi glyph là một ký tự rune rõ ràng, không phải chấm tròn).
GLYPHS=[
 ["..g..",".ggg.","g..g.","ggggg","g...g"],
 ["g...g",".g.g.","..g..",".g.g.","g...g"],
 [".ggg.","g...g","..g..","..g..","..g.."],
 ["gg.gg","g.g.g","..g..","g.g.g","gg.gg"],
 ["..g..","..g..","ggggg","..g..","..g.."],
 ["ggggg","g....","gggg.","g....","ggggg"],
 [".g.g.",".g.g.","ggggg",".g.g.",".g.g."],
 ["g...g","gg.gg","g.g.g","g..gg","g...g"],
]

def glyph(c,x,y,rows,col):
    for j,row in enumerate(rows):
        for k,ch in enumerate(row):
            if ch=='g': c.pixel(x+k-2,y+j-2,col)

def frame(i):
    c=Canvas(SIZE,SIZE)
    r=[9,14,18,20,19,14][i]
    # vòng đôi + các vạch nối glyph
    c.ellipse(CX-r,CY-r,CX+r,CY+r,DIM if i in(0,5) else RING,False)
    c.ellipse(CX-r+5,CY-r+5,CX+r-5,CY+r-5,RING if i in(0,5) else RUNE,False)
    glow = i in (1,2,4)
    for a in range(0,360,45):
        t=math.radians(a)
        gx=round(CX+(r-2)*math.cos(t)); gy=round(CY+(r-2)*math.sin(t))
        ix=round(CX+(r-8)*math.cos(t)); iy=round(CY+(r-8)*math.sin(t))
        c.line(ix,iy,gx,gy,RUNE if glow else DIM,1)
        c.pixel(gx,gy,LIT if glow else DIM)
    # 8 glyph trên vòng
    for n,a in enumerate(range(0,360,45)):
        t=math.radians(a)
        gx=round(CX+(r+4)*math.cos(t)); gy=round(CY+(r+4)*math.sin(t))
        col = WHITE if i in (2,4) else LIT if glow else RUNE if i==3 else DIM
        glyph(c,gx,gy,GLYPHS[n],col)
    # nhịp tim ở tâm: sao 4 cánh phình/thu
    cr=[1,2,4,2,4,2][i]
    c.ellipse(CX-cr,CY-cr,CX+cr,CY+cr,LIT if glow else RUNE)
    c.pixel(CX,CY,WHITE if i in (2,4) else CYAN)
    for dx,dy in ((cr+2,0),(-(cr+2),0),(0,cr+2),(0,-(cr+2))):
        c.pixel(CX+dx,CY+dy,CYAN if glow else DIM)
    return c

ANIM=[("spell", [frame(i) for i in range(6)], 12, False,
       {"hitbox":{"shape":"circle","center":[32.0,32.0],"active":[1,4]}})]
if __name__=="__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print(f"OK {NAME}")
