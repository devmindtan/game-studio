#!/usr/bin/env python3
"""Mũ trùm sát thủ (giáp da tối)."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="assassin-hood"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
DARK="#2a2438"; D_D="#171320"; D_L="#4a3f5c"; TRIM="#8b3a62"; EYE="#b06cff"
def hood(c,glow=0):
    c.ellipse(7,6,21,22,D_D); c.ellipse(8,7,20,21,DARK)
    c.polygon([(14,3),(7,11),(21,11)],DARK); c.line(14,3,9,10,D_L)
    c.ellipse(10,12,18,20,D_D); c.ellipse(11,13,17,19,"#0d0b14")
    c.line(12,16,14,16,EYE if glow else "#3a2a4a"); c.line(14,16,16,16,EYE if glow else "#3a2a4a")
    c.line(9,20,19,20,TRIM); c.polygon([(14,5),(12,9),(16,9)],TRIM)
def idle(i):
    c=Canvas(W,H); c.ellipse(8,21,20,23,"#00000033")
    hood(c, glow=1 if i in (2,3,4) else 0)
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
