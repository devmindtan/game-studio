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

# Rune field: glyph ring draws in, pulses twice, then vanishes.
PALETTE=["#301c58","#5b3194","#9456d1","#d287ff","#f2d6ff","#68e8ff"]
def frame(i):
 c=Canvas(SIZE,SIZE)
 r=[8,13,18,20,19,15][i]
 c.ellipse(32-r,32-r,32+r,32+r,PALETTE[1],False)
 c.ellipse(32-(r-4),32-(r-4),32+(r-4),32+(r-4),PALETTE[2],False)
 for a in range(0,360,45):
  t=math.radians(a+i*2); x=round(32+r*math.cos(t)); y=round(32+r*math.sin(t))
  ix=round(32+(r-4)*math.cos(t)); iy=round(32+(r-4)*math.sin(t))
  c.line(ix,iy,x,y,PALETTE[3],1)
  tx=round(32+(r+2)*math.cos(t)); ty=round(32+(r+2)*math.sin(t)); c.pixel(tx,ty,PALETTE[4])
 # Four directional rune chevrons and a bright center pulse.
 for sx,sy in ((1,0),(-1,0),(0,1),(0,-1)):
  x=32+sx*(r-8); y=32+sy*(r-8); c.pixel(x,y,PALETTE[5]); c.pixel(x-sy,y+sx,PALETTE[3])
 if i in (1,2,3,4):
  cr=[2,3,4,3,2,1][i]; c.ellipse(32-cr,32-cr,32+cr,32+cr,PALETTE[4])
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
