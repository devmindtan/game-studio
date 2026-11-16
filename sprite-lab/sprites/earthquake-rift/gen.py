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

# Ground shock: radial cracks open, lift angular rock chips, settle.
PALETTE=["#302a35","#65434a","#9b5e49","#d09354","#f1cf7a","#fff0bb"]
def frame(i):
 c=Canvas(SIZE,SIZE)
 reach=[5,10,15,20,22,18][i]
 for a in range(0,360,45):
  rad=math.radians(a+(i%2)*4); ex=round(32+reach*math.cos(rad)); ey=round(32+reach*math.sin(rad))
  mx=round(32+reach*.55*math.cos(rad+.10)); my=round(32+reach*.55*math.sin(rad+.10))
  c.line(32,32,mx,my,PALETTE[0],3); c.line(mx,my,ex,ey,PALETTE[1],2)
  c.line(32,32,mx,my,PALETTE[3],1)
  if i in (2,3,4):
   side=3+(i%2); x=round(32+(reach+side)*math.cos(rad+.20)); y=round(32+(reach+side)*math.sin(rad+.20))
   c.polygon([(x,y-2),(x+3,y),(x,y+2),(x-2,y)],PALETTE[2])
   c.pixel(x,y-1,PALETTE[4])
 if i<4:
  c.ellipse(28,28,36,36,PALETTE[4]); c.ellipse(30,30,34,34,PALETTE[5])
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
