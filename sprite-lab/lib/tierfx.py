"""Tiers II-V for a skill sprite that has one look (user 2026-11-17: the newer
skills had no level designs). Tier I is the existing sprite; each next tier keeps
everything of the one before (pixel-sprite rule: tiers inherit) and adds one idea:
  II   a glow round the outline
  III  sparks flying round the shape
  IV   a second, dotted energy shell further out
  V    light rays out of the shape and a white-hot core
thin=True (art of thin lines: cracks, rings, bolts): the glow and the shell stay out of
the 1-2 px gaps between lines, so the lines do not merge into a blob.
Every animation of the base (16 flight directions included) is kept; frames get a
margin so nothing is clipped; hitboxes are measured again from the pixels, so a
tier's glow and shell widen its hit area a little, as they widen its look.
"""
import json
import math
from collections import deque
from pathlib import Path

from PIL import Image

from spritekit import Canvas

PAD = 6
HIT = 96


def _load(base_dir: Path, base: str):
    meta = json.loads((base_dir / f"{base}.json").read_text())
    strip = Image.open(base_dir / f"{base}_strip.png").convert("RGBA")
    fw, fh = meta["frame_size"]
    frames = [strip.crop((i * fw, 0, i * fw + fw, fh)) for i in range(strip.width // fw)]
    return meta, frames


def _rgba(hex_col, a=255):
    h = hex_col.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _dist(img):
    """Chebyshev distance of every pixel to the solid shape (alpha >= HIT)."""
    w, h = img.size
    px = img.load()
    d = [[99] * w for _ in range(h)]
    q = deque()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] >= HIT:
                d[y][x] = 0
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and d[ny][nx] > d[y][x] + 1:
                    d[ny][nx] = d[y][x] + 1
                    q.append((nx, ny))
    return d


def _mass_dist(d, W, H):
    """thin mode: distance to the art closed into one mass (gaps up to 4 px filled:
    dilate 2, erode 2; holes filled), so the glow and shell go round the whole effect, not between
    its lines."""
    dil = [[d[y][x] <= 2 for x in range(W)] for y in range(H)]
    q = deque()
    m = [[99] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if dil[y][x] and all(0 <= x + dx < W and 0 <= y + dy < H and dil[y + dy][x + dx]
                                 for dx in range(-2, 3) for dy in range(-2, 3)):
                m[y][x] = 0
                q.append((x, y))
            elif d[y][x] == 0:
                m[y][x] = 0
                q.append((x, y))
    # fill the holes: anything not reachable from the frame edge through open pixels is mass
    out = [[False] * W for _ in range(H)]
    fq = deque((x, y) for x in range(W) for y in (0, H - 1)) + deque((x, y) for y in range(H) for x in (0, W - 1))
    while fq:
        x, y = fq.popleft()
        if 0 <= x < W and 0 <= y < H and not out[y][x] and m[y][x] != 0:
            out[y][x] = True
            fq.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for y in range(H):
        for x in range(W):
            if not out[y][x] and m[y][x] != 0:
                m[y][x] = 0
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and m[ny][nx] > m[y][x] + 1:
                    m[ny][nx] = m[y][x] + 1
                    q.append((nx, ny))
    return m


def tier_frame(src, tier, i, light, glow, thin=False):
    w, h = src.size
    img = Image.new("RGBA", (w + 2 * PAD, h + 2 * PAD), (0, 0, 0, 0))
    img.alpha_composite(src, (PAD, PAD))
    if img.getbbox() is None:
        return img
    d = _dist(img)
    px = img.load()
    W, H = img.size
    bb = img.getbbox()
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    rx, ry = (bb[2] - bb[0]) / 2, (bb[3] - bb[1]) / 2
    if thin:
        d = _mass_dist(d, W, H)
    if tier >= 4:   # dotted shell 3 px out
        for y in range(H):
            for x in range(W):
                if d[y][x] == 3 and (x + y + i) % 3 == 0 and px[x, y][3] == 0:
                    px[x, y] = _rgba(glow, 150)
    if tier >= 2:   # glow hugging the outline
        for y in range(H):
            for x in range(W):
                if d[y][x] == 1 and px[x, y][3] < 60:
                    px[x, y] = _rgba(glow, 170)
    if tier >= 3:   # sparks round the shape
        for k in range(6):
            a = k * 2.39 + i * 0.7
            x = int(round(cx + math.cos(a) * (rx + 3)))
            y = int(round(cy + math.sin(a) * (ry + 3)))
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = _rgba(light)
                if 0 <= x + 1 < W:
                    px[x + 1, y] = _rgba(glow, 160)
    if tier >= 5:   # rays and a white-hot core
        for k in range(8):
            a = k * math.pi / 4 + (i % 2) * 0.2
            l0 = max(rx, ry) * 0.8
            ln = 3 + (k + i) % 3
            for t in range(ln):
                x = int(round(cx + math.cos(a) * (l0 + t)))
                y = int(round(cy + math.sin(a) * (l0 + t)))
                if 0 <= x < W and 0 <= y < H and px[x, y][3] < HIT:
                    px[x, y] = _rgba(light, 230 - t * 30)
        for y in range(H):
            for x in range(W):
                r, g, b, a = px[x, y]
                if a >= HIT and r + g + b > 700:   # only the brightest core turns white
                    px[x, y] = (255, 255, 255, a)
    return img


def build(here: Path, base: str, tier: int, light: str, glow: str, export_fn, thin=False):
    base_dir = here.parent / base
    meta, frames = _load(base_dir, base)
    anims = []
    for a in meta["animations"]:
        out = []
        for k in range(a["frames"]):
            c = Canvas(1, 1)
            c.img = tier_frame(frames[a["start"] + k], tier, k, light, glow, thin)
            out.append(c)
        extra = {}
        if "durations_ms" in a:
            extra["durations_ms"] = a["durations_ms"]
        hb = a.get("hitbox")
        if hb:
            spec = {"shape": hb["shape"], "center": [hb["center"][0] + PAD, hb["center"][1] + PAD], "active": hb["active"]}
            if "dir_deg" in hb:
                spec["dir_deg"] = hb["dir_deg"]
            if hb.get("swept"):   # a solid cone carries over to the tiers
                spec["swept"] = True
            extra["hitbox"] = spec
        anims.append((a["name"], out, a["fps"], a["loop"], extra))
    ax, ay = meta["anchor"]
    export_fn(here, here.name, anims, anchor=(ax + PAD, ay + PAD))
    if "px_scale" in meta:   # a double-density base keeps its density in every tier
        out = here / f"{here.name}.json"
        m = json.loads(out.read_text())
        m["px_scale"] = meta["px_scale"]
        out.write_text(json.dumps(m, indent=2) + "\n")
