#!/usr/bin/env python3
"""Authored pixel AOE effect for Sprite Lab; see animation and hitbox metadata."""
import math, sys
from pathlib import Path

def _workspace():
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists(): return parent
    raise SystemExit("workspace not found")
sys.path.insert(0, str(_workspace()/"tools/gamekit/pipeline"))
from spritekit import Canvas, gif, preview, strip, write_anim_meta
NAME=Path(__file__).parent.name
SIZE=64; CX=CY=32; ANCHOR=(32.0,32.0); HERE=Path(__file__).parent

# Storm field: several staggered lightning strikes inside a charged circular boundary.
PALETTE=["#34265f","#5945a4","#7969dc","#a6b5ff","#f2f5ff","#72e8ff"]
def bolt(c,x,y,scale,phase):
 pts=[(x,y-9*scale),(x-3*scale,y-2*scale),(x+1*scale,y-2*scale),(x-4*scale,y+8*scale),(x+4*scale,y),(x,y)]
 pts=[(round(a),round(b)) for a,b in pts]
 for p,q in zip(pts,pts[1:]): c.line(*p,*q,PALETTE[1],3)
 for p,q in zip(pts,pts[1:]): c.line(*p,*q,PALETTE[4],1)
 c.pixel(x,y+9*scale,PALETTE[5])
def frame(i):
 c=Canvas(SIZE,SIZE)
 r=[11,17,22,24,21,14][i]
 c.ellipse(32-r,32-r,32+r,32+r,PALETTE[0],False)
 c.ellipse(32-r+2,32-r+2,32+r-2,32+r-2,PALETTE[1],False)
 # Split strikes across frames, but each active frame has a readable impact.
 points=[(24,24),(40,23),(25,41),(40,40)]
 for n,(x,y) in enumerate(points):
  if (i+n)%3 != 0 and i in (1,2,3,4): bolt(c,x,y,1,(i+n)%2)
 for a in range(0,360,45):
  x=round(32+(r-2)*math.cos(math.radians(a))); y=round(32+(r-2)*math.sin(math.radians(a)))
  c.pixel(x,y,PALETTE[3]); c.pixel(x+1,y,PALETTE[5])
 return c

FRAMES=[frame(i) for i in range(6)]
def main():
 strip(FRAMES).save(HERE/f"{NAME}_strip.png")
 FRAMES[0].save(HERE/f"{NAME}.png")
 preview([strip(FRAMES)],HERE/"preview.png",scale=4)
 gif(FRAMES,HERE/"spell.gif",fps=12,scale=3)
 write_anim_meta(HERE/f"{NAME}.json",[{
  "name":"spell","frames":FRAMES,"fps":12,"loop":False,
  "hitbox":{"shape":"circle","center":[32.0,32.0],"active":[1,4]}
 }],anchor=ANCHOR)
 print(f"preview: {HERE/'preview.png'}")
if __name__=="__main__": main()
