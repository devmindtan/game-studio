#!/usr/bin/env python3
"""Mũ trùm pháp sư (giáp vải)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="mage-hood"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CLOTH="#4a2a7a"; CLOTH_D="#301f58"; CLOTH_L="#6d47ad"; TRIM="#c9a4f2"; STAR="#7ef0ff"; CORE="#ffffff"
def hood(c,glow=0):
    c.ellipse(7,6,21,22,CLOTH_D); c.ellipse(8,7,20,21,CLOTH)
    c.polygon([(14,4),(8,10),(20,10)],CLOTH); c.line(14,4,10,9,CLOTH_L); c.line(14,4,18,9,CLOTH_D)
    # face shadow
    c.ellipse(10,12,18,20,CLOTH_D)
    c.ellipse(11,13,17,19,"#1a1028")
    # trim
    c.line(9,20,19,20,TRIM); c.line(10,21,18,21,TRIM)
    # rune
    p=c.pixel; p(14,8,STAR if glow else TRIM)
    if glow:
        p(13,8,STAR); p(15,8,STAR); p(14,7,CORE)
def idle(i):
    c=Canvas(W,H); c.ellipse(8,21,20,23,"#00000033")
    hood(c, glow=1 if i in (2,3) else 0)
    return c
ANIMATIONS=[("idle",[idle(0)],1,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=6)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=6)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp,"hitbox":{"shape":"rect","center":[float(ANCHOR[0]),float(ANCHOR[1])],"active":[0,len(f)-1]}} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/f"preview.png")
if __name__=="__main__": main()
