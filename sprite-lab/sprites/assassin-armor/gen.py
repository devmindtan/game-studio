#!/usr/bin/env python3
"""Giáp sát thủ (da tối)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="assassin-armor"; W,H=32,32; ANCHOR=(16.0,30.0); HERE=Path(__file__).resolve().parent; OUT=HERE
DARK="#2a2438"; D_D="#171320"; D_L="#4a3f5c"; TRIM="#8b3a62"; METAL="#5f7187"
def armor(c,glint=False):
    c.polygon([(11,7),(21,7),(24,27),(8,27)],D_D)
    c.polygon([(12,8),(20,8),(23,26),(9,26)],DARK)
    c.ellipse(8,7,13,13,D_D); c.ellipse(19,7,24,13,D_D)
    c.polygon([(14,7),(18,7),(16,11)],D_D); c.line(14,7,16,11,TRIM); c.line(18,7,16,11,TRIM)
    c.rect(10,20,22,23,D_D); c.rect(14,20,18,22,TRIM)
    c.line(16,11,16,19,D_L)
    # straps
    c.line(12,10,20,18,D_L); c.line(20,10,12,18,D_L)
    c.rect(15,13,17,15,METAL)
    if glint: c.pixel(15,14,"#9aa4b8")
def idle(i):
    c=Canvas(W,H); c.ellipse(9,29,23,31,"#00000033")
    armor(c, glint=(i==3))
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
