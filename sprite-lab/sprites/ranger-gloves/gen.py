#!/usr/bin/env python3
"""Găng ranger (da nhẹ)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="ranger-gloves"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
LEATHER="#6b8f3a"; L_D="#3f5a22"; L_L="#8fb84d"; TRIM="#c4a45a"
def glove(c,x,flip=False,glint=False):
    dx=-1 if flip else 1
    c.rect(min(x,x+4*dx),10,max(x,x+4*dx),18,L_D)
    c.rect(min(x+dx,x+3*dx),11,max(x+dx,x+3*dx),17,LEATHER)
    for i in range(3): c.rect(min(x+i*dx,x+i*dx+dx),7,max(x+i*dx,x+i*dx+dx),10,LEATHER)
    c.rect(min(x+3*dx,x+4*dx),8,max(x+3*dx,x+4*dx),10,LEATHER)
    c.rect(min(x-dx,x+4*dx),18,max(x-dx,x+4*dx),20,L_D)
    c.line(min(x-dx,x+4*dx),18,max(x-dx,x+4*dx),18,TRIM)
    c.line(x+2*dx,12,x+2*dx,15,L_D)
    if glint: c.pixel(x+dx,11,L_L)
def idle(i):
    c=Canvas(W,H); c.ellipse(6,21,22,23,"#00000033")
    gl=i==2
    glove(c,7,False,gl); glove(c,20,True,gl)
    return c
ANIMATIONS=[("idle",[idle(i) for i in range(6)],6,True)]
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
