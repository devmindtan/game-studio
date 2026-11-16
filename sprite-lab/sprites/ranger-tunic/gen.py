#!/usr/bin/env python3
"""Áo giáp ranger (da nhẹ)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="ranger-tunic"; W,H=32,32; ANCHOR=(16.0,30.0); HERE=Path(__file__).resolve().parent; OUT=HERE
LEATHER="#6b8f3a"; L_D="#3f5a22"; L_L="#8fb84d"; CLOTH="#5a4632"; TRIM="#c4a45a"
def tunic(c,glint=False):
    c.polygon([(11,7),(21,7),(24,26),(8,26)],L_D)
    c.polygon([(12,8),(20,8),(23,25),(9,25)],LEATHER)
    c.ellipse(8,7,13,13,L_D); c.ellipse(19,7,24,13,L_D)
    c.rect(10,22,22,25,CLOTH)
    c.line(10,22,22,22,TRIM)
    c.rect(14,22,18,25,TRIM)
    c.line(16,9,16,21,L_D)
    c.line(12,10,16,13,TRIM); c.line(20,10,16,13,TRIM)
    c.polygon([(14,7),(18,7),(16,11)],CLOTH)
    if glint: c.pixel(13,9,L_L)
def idle(i):
    c=Canvas(W,H); c.ellipse(9,29,23,31,"#00000033")
    tunic(c, glint=(i in (1,2)))
    return c
ANIMATIONS=[("idle",[idle(i) for i in range(6)],6,True)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=5)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=5)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/f"preview.png")
if __name__=="__main__": main()
