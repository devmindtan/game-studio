#!/usr/bin/env python3
"""Mũ ranger (giáp da nhẹ)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="ranger-cap"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
LEATHER="#6b8f3a"; L_D="#3f5a22"; L_L="#8fb84d"; TRIM="#c4a45a"; FEATHER="#2f6b3a"
def cap(c,glint=False):
    c.ellipse(8,8,20,22,L_D); c.ellipse(9,9,19,21,LEATHER)
    c.line(8,14,20,14,L_D)
    # brim
    c.ellipse(6,14,22,18,L_D); c.ellipse(7,15,21,17,L_L)
    c.line(7,16,21,16,LEATHER)
    # feather
    c.line(18,7,22,3,FEATHER); c.line(19,7,23,4,FEATHER); c.line(17,8,21,5,FEATHER)
    c.rect(13,13,15,14,TRIM)
    if glint: c.pixel(10,10,L_L)
def idle(i):
    c=Canvas(W,H); c.ellipse(8,21,20,23,"#00000033")
    cap(c, glint=(i==2))
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
