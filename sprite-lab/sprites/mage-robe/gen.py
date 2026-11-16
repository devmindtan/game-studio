#!/usr/bin/env python3
"""Áo choàng pháp sư (giáp vải)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="mage-robe"; W,H=32,32; ANCHOR=(16.0,30.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CLOTH="#4a2a7a"; CLOTH_D="#301f58"; CLOTH_L="#6d47ad"; TRIM="#c9a4f2"; GOLD="#d9b44a"; RUNE="#7ef0ff"
def robe(c,glow=0):
    c.polygon([(10,6),(22,6),(26,28),(6,28)],CLOTH_D)
    c.polygon([(11,7),(21,7),(25,27),(7,27)],CLOTH)
    # shoulders
    c.ellipse(7,6,13,12,CLOTH_D); c.ellipse(19,6,25,12,CLOTH_D)
    c.line(11,8,21,8,TRIM)
    # collar
    c.polygon([(13,6),(19,6),(16,10)],CLOTH_D); c.line(13,6,16,10,TRIM); c.line(19,6,16,10,TRIM)
    # belt
    c.rect(9,18,23,20,CLOTH_D); c.rect(14,18,18,20,GOLD)
    c.line(9,18,23,18,TRIM)
    # hem trim
    c.line(7,27,25,27,TRIM); c.line(8,28,24,28,TRIM)
    # rune lines
    c.line(16,11,16,17,RUNE if glow else TRIM)
    c.line(13,14,19,14,RUNE if glow else CLOTH_L)
    if glow: c.pixel(16,14,"#ffffff")
    # fold
    c.line(12,12,10,26,CLOTH_D); c.line(20,12,22,26,CLOTH_L)
def idle(i):
    c=Canvas(W,H); c.ellipse(8,29,24,31,"#00000033")
    robe(c, glow=1 if i in (2,3) else 0)
    return c
ANIMATIONS=[("idle",[idle(0)],1,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=5)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=5)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp,"hitbox":{"shape":"rect","center":[float(ANCHOR[0]),float(ANCHOR[1])],"active":[0,len(f)-1]}} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/f"preview.png")
if __name__=="__main__": main()
