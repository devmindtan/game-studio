#!/usr/bin/env python3
"""Ủng pháp sư (giáp vải)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="mage-boots"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CLOTH="#4a2a7a"; CLOTH_D="#301f58"; CLOTH_L="#6d47ad"; TRIM="#c9a4f2"; SOLE="#2b1a33"
def boot(c,x,glow=0):
    c.rect(x,10,x+5,18,CLOTH_D); c.rect(x+1,11,x+4,17,CLOTH)
    c.line(x+1,11,x+4,11,TRIM)
    c.polygon([(x,10),(x+5,10),(x+6,14),(x-1,14)],CLOTH_L)
    c.rect(x-1,18,x+6,20,CLOTH_D); c.rect(x-1,20,x+6,22,SOLE)
    c.line(x+2,13,x+3,16,TRIM if not glow else "#7ef0ff")
def idle(i):
    c=Canvas(W,H); c.ellipse(6,21,22,23,"#00000033")
    gl=1 if i==3 else 0
    boot(c,7,gl); boot(c,16,gl)
    return c
ANIMATIONS=[("idle",[idle(0)],1,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=6)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=6)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/f"preview.png")
if __name__=="__main__": main()
