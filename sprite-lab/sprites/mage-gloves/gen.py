#!/usr/bin/env python3
"""Găng tay pháp sư (giáp vải)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="mage-gloves"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CLOTH="#4a2a7a"; CLOTH_D="#301f58"; CLOTH_L="#6d47ad"; TRIM="#c9a4f2"; RUNE="#7ef0ff"
def glove(c,x,flip=False,glow=0):
    dx=-1 if flip else 1
    c.rect(min(x,x+4*dx),10,max(x,x+4*dx),18,CLOTH_D)
    c.rect(min(x+dx,x+3*dx),11,max(x+dx,x+3*dx),17,CLOTH)
    c.line(x+2*dx,11,x+2*dx,16,TRIM)
    # fingers
    for i in range(3): c.rect(min(x+i*dx,x+i*dx+dx),7,max(x+i*dx,x+i*dx+dx),10,CLOTH)
    c.rect(min(x+3*dx,x+4*dx),8,max(x+3*dx,x+4*dx),10,CLOTH)
    c.rect(min(x-dx,x+4*dx),18,max(x-dx,x+4*dx),20,CLOTH_D)
    c.line(min(x-dx,x+4*dx),18,max(x-dx,x+4*dx),18,TRIM)
    if glow: c.pixel(x+2*dx,13,RUNE)
def idle(i):
    c=Canvas(W,H); c.ellipse(6,21,22,23,"#00000033")
    gl=1 if i in (2,3) else 0
    glove(c,7,False,gl); glove(c,20,True,gl)
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
