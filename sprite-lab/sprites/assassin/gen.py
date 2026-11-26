#!/usr/bin/env python3
"""assassin: the user's own assassin (sprite-lab/sources/user/assassin-2026-11-25.png, user 2026-11-25). Only
animated: the drawing is cut into layers, mirrored to face right, moved by whole pixels (no redrawing). Slots (user
2026-11-25): head (hood), chest, weapon (dagger), feet, arms (gloves). Gloves and boots stay as small as drawn
(user: "vẽ nhỏ nhỏ là được, đừng vẽ nó to lên"). Animations as the other heroes: idle 4, run 8, hurt 3, dash 5,
death 5. Chạy: gamekit art run assassin
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

SRC = WS / "sprite-lab/sources/user/assassin-2026-11-25.png"
S = 48
CROP = (0, 8, 24, 32)
FEET_Y = 22          # the lowest row of the feet (with their outline), crop coords
FLOOR = 44

LAYER_ORDER = ["feet_back", "chest", "body", "head", "arms_front", "weapon"]
SLOT_OF = {"head": "head", "chest": "chest", "feet_back": "feet", "weapon": "weapon", "arms_front": "arms"}
SKIN = {(0xce, 0x92, 0x64), (0xe6, 0xad, 0x84), (0xff, 0xc8, 0x95), (0xe0, 0x84, 0x74), (0, 0, 0)}
BROWN = {(0x4e, 0x31, 0x21), (0x78, 0x4a, 0x32)}
BLACK = (0x08, 0x08, 0x0c)


def _layer_of(x, y, rgb):
    """Layer of a pixel of the user's assassin, in the drawing's own (left-facing) coords."""
    if y >= 28:
        return "feet_back"                                # boots
    if x <= 9 or (x == 21 and 22 <= y <= 25):
        return "weapon"                                   # the dagger in the front hand, the hilt in the back one
    if rgb in BROWN and ((10 <= x <= 11 and 24 <= y <= 25) or (x == 21 and y == 26)):
        return "arms_front"                               # the two small gloves
    if rgb in SKIN:
        return "body"                                     # face
    if y <= 20:
        return "head"                                     # the hood
    return "chest"                                        # tunic, belt, legs


def _group(layer, x, y=0):
    """Motion group (mirrored-crop coords): feet a / b, the head, the rest of the body with what its hands hold."""
    if layer == "feet_back":
        return "a" if x >= 7 else "b"
    if layer == "head" or layer == "body":
        return "hd"
    return "ch"


def _parts():
    im = Image.open(SRC).convert("RGBA")
    out = {k: Image.new("RGBA", (CROP[2] - CROP[0], CROP[3] - CROP[1])) for k in LAYER_ORDER}
    for y in range(CROP[1], CROP[3]):
        for x in range(CROP[0], CROP[2]):
            p = im.getpixel((x, y))
            if p[3]:
                out[_layer_of(x, y, p[:3])].putpixel((x - CROP[0], y - CROP[1]), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT
    return {k: v.transpose(flip) for k, v in out.items()}


PARTS = _parts()
OX = 24 - 7             # after the mirror the feet are x 3..11: centre them on the anchor
OY = FLOOR - FEET_Y - 1


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False, gear=None, hd=(0, 0), wp=(0, 0), ch=(0, 0)):
    """One frame as {layer: Canvas}; gear maps a slot to a colour function (the item tier). up moves the whole upper
    body; hd / ch / wp add to the head, the body and the staff on top of it."""
    offs = {"a": a, "b": b, "hd": (up[0] + hd[0], up[1] + hd[1]), "ch": (up[0] + ch[0], up[1] + ch[1]),
            "wp": (up[0] + wp[0], up[1] + wp[1])}
    out = {}
    for k in LAYER_ORDER:
        fn = (gear or {}).get(SLOT_OF.get(k, ""))
        src = PARTS[k]
        if fn and k == "head" and getattr(fn, "extra", None):   # tier details on the hood
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
                dx, dy = offs[_group(k, x, y)]
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
    # idle: breathe (body dips, the head nods a beat later). The daggers move only with the hands holding them
    idle = [f(), f(hd=(0, 1)), f(up=(0, 1)), f(hd=(0, 1))]
    # run: head locked to the body (the archer's sliding head looked bad, user 2026-11-25); the body dips on each
    # contact, the legs swap with the back foot lifted on the passing frames
    run = [f(up=(0, 1), a=(1, 0), b=(-1, 0)),
           f(up=(0, 1), a=(0, 0), b=(-1, -1)),
           f(a=(0, 0), b=(0, -1)),
           f(a=(-1, 0), b=(1, -1)),
           f(up=(0, 1), a=(-1, 0), b=(1, 0)),
           f(up=(0, 1), a=(-1, -1), b=(0, 0)),
           f(a=(0, -1), b=(0, 0)),
           f(a=(1, -1), b=(-1, 0))]
    hurt = [f(up=(-1, 0), flash=True, hd=(-1, 0)), f(up=(-1, 0), hd=(-1, 1)), f(hd=(0, 1))]
    dash = [f(up=(0, 1), hd=(0, 1)), f(up=(2, 1), a=(2, 0), b=(-2, 0), hd=(1, 0)),
            f(up=(2, 1), a=(2, 0), b=(-2, -1), hd=(1, 0)),
            f(up=(2, 1), a=(2, 0), b=(-2, 0), hd=(1, 0)), f(up=(1, 0))]
    death = [f(up=(-1, 0), flash=True), f(up=(0, 1)), f(up=(0, 1)), lying(f(up=(0, 1))), lying(f(up=(0, 1)))]
    hb = {"shape": "rect", "center": [24.0, 30.0]}
    return [("idle", idle, 5, True, {"durations_ms": [240, 160, 240, 160], "hitbox": dict(hb, active=[0, 3])}),
            ("run", run, 12, True, {"hitbox": dict(hb, active=[0, 7])}),
            ("hurt", hurt, 12, False, {"durations_ms": [90, 110, 120], "hitbox": dict(hb, active=[0, 2])}),
            ("dash", dash, 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": dict(hb, active=[0, 4])}),
            ("death", death, 8, False, {"durations_ms": [120, 140, 140, 100, 400], "hitbox": dict(hb, active=[0, 4])})]


# --- equipment tiers: tier 1 is the user's own colours; the others recolour the drawing's ramps -------------------
# c* cloth ramp (hood, tunic), m* blade metal, t* trims (hilt, belt), b* leather (gloves, boots)
TIERS = {
    "dusk": None,
    "night": {"d": "#1a1c24", "m": "#2c3040", "l": "#444a5e", "h": "#626a82", "M": "#8a94a6", "Mh": "#d8e0ea",
              "t": "#7a7f8c", "T": "#b8bec8", "b": "#2a2228", "B": "#463a40"},
    "blood": {"d": "#3a0c14", "m": "#6a1622", "l": "#962232", "h": "#c03a44", "M": "#9a9a9a", "Mh": "#e8e8e8",
              "t": "#2a2a2a", "T": "#5a5a5a", "b": "#2a1414", "B": "#4a2020"},
    "phantom": {"d": "#0e3a3a", "m": "#1c6464", "l": "#2e9090", "h": "#7ad8d0", "M": "#a8f0ff", "Mh": "#ffffff",
                "t": "#c89a2e", "T": "#ffe08a", "b": "#e0e4ea", "B": "#a0a8b8"},
}
TIER_ORDER = ["dusk", "night", "blood", "phantom"]
ITEMS = {"head": ["dusk_hood", "night_hood", "blood_hood", "phantom_hood"],
         "chest": ["dusk_tunic", "night_tunic", "blood_tunic", "phantom_tunic"],
         "weapon": ["dusk_dagger", "night_dagger", "blood_dagger", "phantom_dagger"],
         "feet": ["dusk_boots", "night_boots", "blood_boots", "phantom_boots"],
         "arms": ["dusk_gloves", "night_gloves", "blood_gloves", "phantom_gloves"]}
HOOD_EXTRA = {"dusk": [], "night": [], "blood": [], "phantom": [(11, 4, "#ffe08a")]}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def recolour(tier):
    if TIERS[tier] is None:                               # the drawing as the user made it
        fn = lambda p: p  # noqa: E731
        fn.extra = []
        return fn
    t = {k: _rgb(v) for k, v in TIERS[tier].items()}
    cloth = [t["d"], t["m"], t["l"], t["h"]]

    def fn(p):
        r, g, b, a = p
        rgb = (r, g, b)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if rgb == BLACK or lum < 25 or rgb in SKIN:
            return p
        if rgb in BROWN:
            return (*(t["B"] if lum > 70 else t["b"]), a)
        if b > r + 30 and b > g + 30:                     # hood / tunic purples -> the tier cloth ramp
            return (*cloth[min(3, int(lum / 30))], a)
        if max(r, g, b) - min(r, g, b) < 18:              # blade greys
            return (*(t["Mh"] if lum > 180 else t["M"]), a)
        if r > b + 20:                                    # khaki hilt, belt, boot trims
            return (*(t["T"] if lum > 150 else t["t"]), a)
        return p

    fn.extra = HOOD_EXTRA[tier]
    return fn


def write_layers(anim_list, names, folder):
    folder.mkdir(parents=True, exist_ok=True)
    every = [fr for _, frames, *_ in anim_list for fr in frames]
    for k in names:
        strip([fr[k] for fr in every]).save(folder / f"{k}_strip.png")


PIECES = {"weapon": (28, 23, 42, 32), "head": (10, 9, 23, 21), "chest": (12, 21, 23, 28)}
GLOVE_PAL = {"d": "#2c1a10", "m": "#4e3121", "l": "#784a32", "h": "#a06a48", "t": "#ada56b"}


def write_icons(folder):
    """Hood, tunic and dagger come from the drawing (the dagger from the user's own icon beside the figure); gloves
    and boots are drawn by lib/drawnicons in the tier leather."""
    import drawnicons
    folder.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            if slot in ("feet", "arms"):
                pal = GLOVE_PAL if TIERS[tier] is None else {"d": TIERS[tier]["b"], "m": TIERS[tier]["b"],
                                                             "l": TIERS[tier]["B"], "h": TIERS[tier]["T"],
                                                             "t": TIERS[tier]["t"]}
                (drawnicons.boots if slot == "feet" else drawnicons.gloves)(pal).save(folder / f"{item}.png")
                continue
            fn = recolour(tier)
            im = src.crop(PIECES[slot])
            if slot == "chest":                           # the tunic is 11 px wide: twice its size reads as an icon
                im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
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
    check_connected(flat_anims, "assassin")
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
            check_connected([(n, [flat(fr) for fr in frames], *r) for n, frames, *r in sets], f"assassin {item}")
            write_layers(sets, meta["slots"][slot], HERE / "gear" / item)
    write_icons(HERE / "icons")
    print("OK", HERE.name, "+ 20 items + icons")
