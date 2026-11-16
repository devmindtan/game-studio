#!/usr/bin/env python3
"""Giáp ủng/chân hiệp sĩ (giáp). idle 6f loop."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="knight-greaves"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
STEEL="#b8c7d9"; STEEL_D="#5f7187"; EDGE="#e8f4ff"; DARK="#3a4657"; GOLD="#d9b44a"; LEATHER="#4a3524"
def boot(c,x,glint=False):
    c.rect(x,8,x+5,18,STEEL_D); c.rect(x+1,9,x+4,17,STEEL)
    c.line(x+1,9,x+4,9,EDGE)
    c.rect(x,14,x+5,15,GOLD)
    # knee
    c.ellipse(x,6,x+5,10,STEEL_D); c.ellipse(x+1,7,x+4,9,STEEL)
    # foot
    c.rect(x-1,18,x+6,21,STEEL_D); c.rect(x,19,x+5,20,STEEL)
    c.rect(x-1,21,x+6,22,DARK)
    c.rect(x+1,11,x+4,12,STEEL_D)
    if glint: c.pixel(x+2,8,EDGE)
def idle(i):
    c=Canvas(W,H); c.ellipse(6,21,22,23,"#00000033")
    gl=i in (1,2)
    boot(c,7,gl); boot(c,16,gl)
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
