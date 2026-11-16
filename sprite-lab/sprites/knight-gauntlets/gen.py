#!/usr/bin/env python3
"""Găng thép hiệp sĩ (giáp). idle 6f loop. Neo đáy."""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
from PIL import Image
NAME="knight-gauntlets"; W,H=28,24; ANCHOR=(14.0,22.0); HERE=Path(__file__).resolve().parent; OUT=HERE
STEEL="#b8c7d9"; STEEL_D="#5f7187"; EDGE="#e8f4ff"; GOLD="#d9b44a"; LEATHER="#6b4a2e"

def gaunt(c,x0,flip=False,glint=False):
    g=Canvas(8,14)
    pts=[(1,2),(5,2),(6,5),(5,10),(3,11),(0,8),(0,4)]
    g.polygon(pts,STEEL_D); g.polygon([(1,3),(4,3),(5,5),(4,9),(3,10),(1,7),(1,4)],STEEL)
    g.line(1,3,4,3,EDGE)
    g.rect(2,5,3,6,GOLD)
    for fy in (7,8,9): g.line(2,fy,4,fy,STEEL_D)
    g.rect(0,10,6,12,LEATHER); g.line(0,10,6,10,GOLD)
    if glint: g.pixel(2,3,EDGE)
    img = g.img.transpose(Image.FLIP_LEFT_RIGHT) if flip else g.img
    c.img.alpha_composite(img, (x0, 7))

def idle(i):
    c=Canvas(W,H); c.ellipse(6,21,22,23,"#00000033")
    gl=i in (2,3)
    gaunt(c,5,False,gl); gaunt(c,16,True,gl)
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
