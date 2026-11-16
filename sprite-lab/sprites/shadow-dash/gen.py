#!/usr/bin/env python3
"""Lướt bóng tối (hệ sát thủ, skill): vệt dịch chuyển/biến mất trong khói tím.

  dash    7 frame một lần: bùng khói bóng tối tại chỗ rồi vệt lướt về trước.

Neo (12, 28) điểm xuất phát (sprite 48x32). Lướt sang phải.
"""
import sys
from pathlib import Path
def _ws():
    for p in Path(__file__).resolve().parents:
        if (p/"tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")
sys.path.insert(0,str(_ws()/"tools/gamekit/pipeline"))
from spritekit import Canvas,gif,preview,strip,write_anim_meta
NAME="shadow-dash"; W,H=48,32; ANCHOR=(12.0,28.0); HERE=Path(__file__).resolve().parent; OUT=HERE
CORE="#e9d5ff"; EDGE="#b06cff"; DARK="#4a1d6b"; SMOKE="#2a1038"; SMOKE2="#1a0c24"
def p(c,x,y,col):
    if 0<=x<W and 0<=y<H: c.pixel(x,y,col)
def puff(c,cx,cy,rx,ry,col):
    c.ellipse(cx-rx,cy-ry,cx+rx,cy+ry,col)
def dash(i):
    c=Canvas(W,H)
    if i==0:
        puff(c,12,24,4,5,SMOKE); puff(c,12,22,3,3,DARK); p(c,12,20,EDGE); return c
    if i==1:
        puff(c,12,23,6,6,SMOKE2); puff(c,12,22,4,4,SMOKE); puff(c,14,21,3,3,DARK); p(c,16,20,EDGE)
        return c
    if i==2:
        puff(c,10,24,5,5,SMOKE2); puff(c,14,22,4,4,SMOKE)
        c.line(16,22,28,20,DARK); c.line(16,23,28,21,SMOKE); c.line(18,22,30,21,EDGE)
        p(c,31,20,CORE)
        return c
    if i==3:
        puff(c,8,25,4,4,SMOKE2)
        c.line(20,22,36,20,SMOKE); c.line(22,22,38,21,DARK); c.line(24,22,40,21,EDGE)
        p(c,41,21,CORE); p(c,39,20,EDGE)
        return c
    if i==4:
        c.line(26,22,40,21,SMOKE2); c.line(28,22,42,21,SMOKE); c.line(30,22,43,21,EDGE)
        puff(c,44,22,3,3,DARK); p(c,44,21,CORE)
        return c
    if i==5:
        c.line(34,22,44,22,SMOKE2); puff(c,44,22,3,3,SMOKE); p(c,44,21,EDGE)
        return c
    puff(c,44,23,2,2,SMOKE2); p(c,44,22,DARK)
    return c
ANIMATIONS=[("dash",[dash(i) for i in range(7)],15,False)]
def main():
    flat=[f for _,fr,_,_ in ANIMATIONS for f in fr]
    strip(flat).save(OUT/f"{NAME}_strip.png"); flat[0].save(OUT/f"{NAME}.png")
    cols=max(len(fr) for _,fr,_,_ in ANIMATIONS); sheet=Canvas(cols*W,len(ANIMATIONS)*H)
    for r,(_,fr,_,_) in enumerate(ANIMATIONS): sheet.paste(strip(fr),0,r*H)
    preview([sheet],HERE/"preview.png",scale=4)
    for a,fr,fps,_ in ANIMATIONS: gif(fr,HERE/f"{a}.gif",fps=fps,scale=4)
    write_anim_meta(OUT/f"{NAME}.json",[{"name":n,"frames":f,"fps":fps,"loop":lp} for n,f,fps,lp in ANIMATIONS],anchor=ANCHOR)
    print(OUT/"preview.png")
if __name__=="__main__": main()
