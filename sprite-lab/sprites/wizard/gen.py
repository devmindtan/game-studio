#!/usr/bin/env python3
"""wizard: the user's own mage (sprite-lab/sources/user/mage-2026-11-25.png, user 2026-11-25: "xử lí tiếp nhân vật
pháp sư"). Only animated: the drawing is cut into the upper body and two feet, mirrored to face right, moved by whole
pixels (no redrawing). Animations as the knight: idle 4, run 8, hurt 3, dash 5, death 5. Equipment layers come later
(the user's choice of slots). Chạy: gamekit art run wizard
"""
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
WS = _ws()
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402
from userart import check_connected  # noqa: E402
from spritekit import strip  # noqa: E402

SRC = WS / "sprite-lab/sources/user/mage-2026-11-25.png"
S = 48
CROP = (0, 0, 32, 30)
FEET_Y = 29          # the lowest row of the feet (with their outline)
FLOOR = 44


LAYER_ORDER = ["feet_back", "chest", "body", "head", "weapon"]
SLOT_OF = {"head": "head", "chest": "chest", "feet_back": "feet", "weapon": "weapon"}
HAIR = {(0xef, 0xef, 0xef), (0xcd, 0xcd, 0xcd), (0x9a, 0x9a, 0x9a), (0xd7, 0xd7, 0xd7), (0x91, 0x91, 0x91)}
SKIN = {(0xf1, 0xbf, 0x92), (0xd1, 0x9b, 0x69), (0xb1, 0x7d, 0x5f)}
STAFF = {(0x78, 0x4a, 0x32), (0x4e, 0x31, 0x21), (0x05, 0x95, 0xe2), (0x78, 0xce, 0xfc), (0x03, 0x65, 0x9a)}
EYE = (0x00, 0xa2, 0xe8)
BLACK = (0x08, 0x08, 0x0c)


def _layer_of(x, y, rgb):
    """Layer of a pixel of the user's mage (left-facing crop). The drawing is the default look (user 2026-11-25:
    the mage wears the robe by default), so every pixel is in some layer."""
    if y >= 27 and x >= 18:
        return "feet_back"
    if rgb in SKIN or rgb in HAIR or rgb == EYE:
        return "body"                                     # face, hair and beard, hands
    if rgb in STAFF or x <= 14 or (x <= 17 and y >= 19 and rgb == BLACK):
        return "weapon"                                   # the staff and its outline
    if y <= 19:
        return "head"                                     # the pointed hood
    return "chest"                                        # the robe


def _group(layer, x):
    if layer == "feet_back":
        return "a" if x >= 10 else "b"                    # mirrored: the left foot is x >= 10
    return "up"


def _parts():
    im = Image.open(SRC).convert("RGBA").crop(CROP)
    out = {k: Image.new("RGBA", im.size) for k in LAYER_ORDER}
    for y in range(im.height):
        for x in range(im.width):
            p = im.getpixel((x, y))
            if p[3]:
                out[_layer_of(x, y, p[:3])].putpixel((x, y), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT
    return {k: v.transpose(flip) for k, v in out.items()}


PARTS = _parts()
OX = 24 - 10            # after the mirror the feet are x 5..13: centre them on the anchor
OY = FLOOR - FEET_Y - 1


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False, gear=None):
    """One frame as {layer: Canvas}; gear maps a slot to a colour function (the item tier)."""
    offs = {"up": up, "a": a, "b": b}
    out = {}
    for k in LAYER_ORDER:
        fn = (gear or {}).get(SLOT_OF.get(k, ""))
        src = PARTS[k]
        if fn and k == "head" and getattr(fn, "extra", None):   # tier details on the hood (user 2026-11-25)
            src = src.copy()
            for (ex, ey, col) in fn.extra:
                src.putpixel((ex, ey), (*_rgb(col), 255))
        px = src.load()
        c = Canvas(S, S)
        for y in range(src.height):
            for x in range(src.width):
                p = px[x, y]
                if not p[3]:
                    continue
                dx, dy = offs[_group(k, x)]
                col = fn(p) if fn else p
                if flash:
                    col = (min(255, col[0] + 150), min(255, col[1] + 150), min(255, col[2] + 150), col[3])
                c.img.putpixel((OX + x + dx, OY + y + dy), col)
        out[k] = c
    return out


def flat(layers):
    c = Canvas(S, S)
    for k in LAYER_ORDER:
        c.img.alpha_composite(layers[k].img)
    return c


def lying(layers):
    whole = flat(layers).img.rotate(90, expand=True)
    bbox = whole.getbbox()
    if not bbox:
        return layers
    w = bbox[2] - bbox[0]
    x0, y0 = max(0, min(S - w, 24 - w // 2)), FLOOR - (bbox[3] - bbox[1])
    out = {}
    for k, c in layers.items():
        n = Canvas(S, S)
        n.img.alpha_composite(c.img.rotate(90, expand=True).crop(bbox), (x0, y0))
        out[k] = n
    return out


def anims(gear=None):
    f = lambda **kw: frame(gear=gear, **kw)  # noqa: E731
    idle = [f(), f(), f(up=(0, 1)), f(up=(0, 1))]
    run = [f(up=(0, 1), a=(1, 0), b=(-1, -1)), f(a=(1, 0), b=(0, -1)), f(a=(0, 0), b=(1, 0)), f(a=(-1, 0), b=(1, 0)),
           f(up=(0, 1), a=(-1, -1), b=(1, 0)), f(a=(0, -1), b=(1, 0)), f(a=(1, 0), b=(0, 0)), f(a=(1, 0), b=(-1, 0))]
    hurt = [f(up=(-1, 0), flash=True), f(up=(-1, 0)), f()]
    dash = [f(up=(0, 1)), f(up=(2, 1), a=(2, 0), b=(-2, 0)), f(up=(2, 1), a=(2, 0), b=(-2, -1)),
            f(up=(2, 1), a=(2, 0), b=(-2, 0)), f(up=(1, 0))]
    death = [f(up=(-1, 0), flash=True), f(up=(0, 1)), f(up=(0, 1)), lying(f(up=(0, 1))), lying(f(up=(0, 1)))]
    hb = {"shape": "rect", "center": [24.0, 30.0]}
    return [("idle", idle, 5, True, {"durations_ms": [240, 160, 240, 160], "hitbox": dict(hb, active=[0, 3])}),
            ("run", run, 12, True, {"hitbox": dict(hb, active=[0, 7])}),
            ("hurt", hurt, 12, False, {"durations_ms": [90, 110, 120], "hitbox": dict(hb, active=[0, 2])}),
            ("dash", dash, 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": dict(hb, active=[0, 4])}),
            ("death", death, 8, False, {"durations_ms": [120, 140, 140, 100, 400], "hitbox": dict(hb, active=[0, 4])})]


# --- equipment tiers: the user's layers recoloured with the mage item icons' ramps (gear-icons PAL "mage") -------
TIERS = {
    "cloth": {"d": "#5a4632", "m": "#8a6e4e", "l": "#b8976a", "h": "#e0c89a", "c": "#6e6e7e", "C": "#4a4a58",
              "b": "#6b4a2b", "B": "#4a321c", "g": "#6fd66a", "G": "#c8ffc0"},
    # arcane in teal: the blue of the icon ramp was too close to the default blue robe (user 2026-11-25)
    "arcane": {"d": "#0f4a52", "m": "#1f7a80", "l": "#35aab0", "h": "#8ee0e0", "c": "#e8e2d0", "C": "#b9b2a0",
               "b": "#8a5a2e", "B": "#563418", "g": "#7ef0ff", "G": "#ffffff"},
    "void": {"d": "#2a1648", "m": "#4a2a80", "l": "#6e48b0", "h": "#a07ae0", "c": "#1b1030", "C": "#120a22",
             "b": "#3a2a4a", "B": "#241830", "g": "#e05aff", "G": "#ffc8ff"},
    "star": {"d": "#10203f", "m": "#1f3b70", "l": "#2f5aa0", "h": "#5a8ad0", "c": "#fff2a8", "C": "#d9a63a",
             "b": "#e8f0f6", "B": "#9fb3c8", "g": "#7ef0ff", "G": "#ffffff"},
}
TIER_ORDER = ["cloth", "arcane", "void", "star"]
ITEMS = {"head": ["cloth_hat", "wizard_hat", "void_hat", "star_hat"],
         "chest": ["cloth_robe", "mage_robe", "void_robe", "star_robe"],
         "feet": ["cloth_shoes", "mage_shoes", "void_shoes", "star_shoes"],
         "weapon": ["wood_staff", "crystal_staff", "void_staff", "star_staff"]}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# details on the hood surface, mirrored-crop coords (frame x - 14, y - 14): pixels inside the hood, so no outline
# changes. void: a small violet gem; star: two gold stars.
HOOD_EXTRA = {"cloth": [], "arcane": [],
              "void": [(9, 8, "#e05aff")],
              "star": [(7, 7, "#fff2a8"), (10, 8, "#fff2a8"), (11, 8, "#d9a63a")]}


def recolour(tier):
    t = {k: _rgb(v) for k, v in TIERS[tier].items()}
    cloth = [t["d"], t["m"], t["l"], t["h"]]

    def fn(p):
        r, g, b, a = p
        rgb = (r, g, b)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if rgb == BLACK or lum < 25:
            return p
        if rgb in STAFF:
            if b > r + 60:                                # the gem
                return (*(t["G"] if lum > 150 else t["g"]), a)
            return (*(t["b"] if lum > 50 else t["B"]), a)   # the wood
        if b > r + 30 and b > g + 30:                     # robe / hood blues and purples -> the tier cloth ramp
            return (*cloth[min(3, int(lum / 32))], a)
        if max(r, g, b) - min(r, g, b) < 18:              # greys: trims, shoes
            return (*(t["c"] if lum > 150 else t["C"]), a)
        return p

    fn.extra = HOOD_EXTRA[tier]
    return fn


def write_layers(anim_list, names, folder):
    folder.mkdir(parents=True, exist_ok=True)
    every = [fr for _, frames, *_ in anim_list for fr in frames]
    for k in names:
        strip([fr[k] for fr in every]).save(folder / f"{k}_strip.png")


KNIGHT_BOOTS = ["iron_boots", "steel_boots", "dragon_boots", "aegis_boots"]
PIECES = {"staff": (38, 5, 53, 29), "hat": (7, 34, 22, 53), "robe": (39, 42, 53, 52)}


def write_icons(folder):
    folder.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    up = lambda im, k: im.resize((im.width * k, im.height * k), Image.NEAREST)  # noqa: E731
    art = {"head": src.crop(PIECES["hat"]), "chest": src.crop(PIECES["robe"]), "weapon": src.crop(PIECES["staff"]),
           "feet": None}   # shoes share the knight's boot icons (user 2026-11-25: too small, same picture, own name)
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            if slot == "feet":
                knight = HERE.parent / "knight" / "icons" / f"{KNIGHT_BOOTS[TIER_ORDER.index(tier)]}.png"
                Image.open(knight).save(folder / f"{item}.png")
                continue
            fn = recolour(tier)
            im = art[slot]
            col = Image.new("RGBA", im.size)
            for yy in range(im.height):
                for xx in range(im.width):
                    p = im.getpixel((xx, yy))
                    if p[3]:
                        col.putpixel((xx, yy), fn(p))
            c = Image.new("RGBA", (24, 24))
            c.alpha_composite(col, ((24 - im.width) // 2, (24 - im.height) // 2))
            c.save(folder / f"{item}.png")


if __name__ == "__main__":
    import json
    base = anims()
    flat_anims = [(n, [flat(fr) for fr in frames], fps, loop, extra) for n, frames, fps, loop, extra in base]
    check_connected(flat_anims, "wizard")
    export(HERE, HERE.name, flat_anims, anchor=(24.0, float(FLOOR)), ground=True, body="idle")
    write_layers(base, LAYER_ORDER, HERE / "layers")
    meta_path = HERE / f"{HERE.name}.json"
    meta = json.loads(meta_path.read_text())
    meta["layers"] = list(LAYER_ORDER)
    meta["outline"] = "none"          # the user's drawing has its own outline
    meta["slots"] = {slot: [k for k, s in SLOT_OF.items() if s == slot] for slot in ITEMS}
    meta["base"] = ["body"]
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            sets = anims({slot: recolour(tier)})
            check_connected([(n, [flat(fr) for fr in frames], *r) for n, frames, *r in sets], f"wizard {item}")
            write_layers(sets, meta["slots"][slot], HERE / "gear" / item)
    write_icons(HERE / "icons")
    print("OK", HERE.name, "+ 16 items + icons")
