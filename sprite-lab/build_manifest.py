#!/usr/bin/env python3
"""Write sprites-manifest.json for the web viewer (viewer.html).

Every image URL carries ?v=<file mtime>, so a sprite that was re-rendered gets a
new URL and the browser cannot show a cached old image (lesson 2026-11-16: the
redrawn mage kept showing the previous art in the viewer).
Run by serve-viewer.sh at start and by `gamekit art run` after each render.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def url(path):
    full = os.path.join(HERE, path)
    v = int(os.path.getmtime(full)) if os.path.exists(full) else 0
    return f"{path}?v={v}"


def build():
    base = os.path.join(HERE, "sprites")
    sprites = []
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        meta_path = os.path.join(d, f"{name}.json")
        if not os.path.isdir(d) or not os.path.exists(meta_path):
            continue
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        entry = {
            "name": name,
            "meta": meta,
            "strip": url(f"sprites/{name}/{name}_strip.png"),
            "preview": url(f"sprites/{name}/preview.png"),
            "thumb": url(f"sprites/{name}/{name}.png"),
            "gifs": {os.path.splitext(os.path.basename(g))[0]: url(f"sprites/{name}/{os.path.basename(g)}")
                     for g in sorted(glob.glob(os.path.join(d, "*.gif")))},
        }
        sprites.append(entry)
    out = os.path.join(HERE, "sprites-manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"sprites": sprites}, f, ensure_ascii=False, indent=2)
    return len(sprites)


if __name__ == "__main__":
    n = build()
    if "--quiet" not in sys.argv:
        print("manifest:", n, "sprites")
