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

# Venom: splatter, spread into a bubbling toxic pool, then recede.
PALETTE=["#183c2b","#28734a","#51b85b","#a6df61","#eaff9a","#d2f34e"]
def frame(i):
 c=Canvas(SIZE,SIZE)
 r=[4,9,14,18,17,12][i]
 if i==0:
  c.ellipse(29,29,35,35,PALETTE[3]); c.pixel(32,32,PALETTE[4])
  for a in range(0,360,45):
   x=round(32+8*math.cos(math.radians(a))); y=round(32+8*math.sin(math.radians(a))); c.pixel(x,y,PALETTE[2])
 else:
  c.ellipse(CX-r,CY-r,CX+r,CY+r,PALETTE[0])
  c.ellipse(CX-r+2,CY-r+2,CX+r-2,CY+r-2,PALETTE[1])
  if i in (2,3,4):
   c.ellipse(CX-r+4,CY-r+4,CX+r-4,CY+r-4,PALETTE[2])
   c.ellipse(CX-r+7,CY-r+7,CX+r-7,CY+r-7,PALETTE[1])
   for a in range(0,360,45):
    x=round(32+(r-5)*math.cos(math.radians(a))); y=round(32+(r-5)*math.sin(math.radians(a)))
    c.pixel(x,y,PALETTE[3]); c.pixel(x+1,y,PALETTE[4])
  for a in range(15,360,60):
   x=round(32+(r-2)*math.cos(math.radians(a))); y=round(32+(r-2)*math.sin(math.radians(a)))
   c.pixel(x,y,PALETTE[5] if (i+a)%2 else PALETTE[3])
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
