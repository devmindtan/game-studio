#!/usr/bin/env python3
"""knight: the user's own knight (sprite-lab/sources/user/knight-2026-11-25.png, user 2026-11-25: "thay nhân vật kiếm
sĩ hiện tại"). The agent only animates it: every frame is the user's pixels, cut into parts and moved by whole pixels
(no redrawing, no smooth rotation). The drawing faces left; it is mirrored so the sheet faces right like the others.

Parts (in the original, left-facing 32x30 crop): left leg x17-19 y26-28, right foot x24-25 y28, everything else is
the upper body (helmet and plume, face, tunic, sword arm and sword, shield).
Animations: idle 4, run 8, hurt 3, dash 5, death 5 (the swordsman's set).
Chạy: gamekit art run knight  ·  thử: gamekit art shot knight sheet|move
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

SRC = WS / "sprite-lab/sources/user/knight-2026-11-25.png"
S = 48
CROP = (0, 0, 32, 30)
FEET_Y = 28            # lowest row of the feet in the crop
FLOOR = 44             # anchor y in the frame (like the swordsman)


LAYER_ORDER = ["legs_back", "feet_back", "chest", "body", "head", "arms_front", "weapon"]
SLOT_OF = {"head": "head", "chest": "chest", "arms_front": "arms", "legs_back": "legs", "feet_back": "feet",
           "weapon": "weapon"}


def _layer_of(x, y, rgb):
    """Which equipment layer an original pixel (left-facing crop) belongs to."""
    if 17 <= x <= 19 and y == 26:
        return "legs_back"
    if (17 <= x <= 19 and 27 <= y <= 28) or (24 <= x <= 25 and y == 28):
        return "feet_back"
    if (x <= 14 and y >= 14) or (x >= 23 and 20 <= y <= 27):
        return "weapon"                                   # the sword, and the shield (sword and board)
    if 15 <= x <= 16 and 21 <= y <= 24:
        return "arms_front"                               # the sword hand
    r, g, b = rgb
    grey = max(r, g, b) - min(r, g, b) < 18 and max(r, g, b) > 60
    if 17 <= x <= 24 and 13 <= y <= 19 and not grey:
        return "body"                                     # face: skin, eyes, mouth, blush
    if y <= 19:
        return "head"                                     # helmet and plume
    return "chest"


def _parts():
    """The original split into layers, mirrored to face right. Returns {layer: Image}."""
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
# after the mirror the feet sit at x 6..14 of the 32-wide crop: centre the pair on the anchor
OX = 24 - 10
OY = FLOOR - FEET_Y - 1   # the feet row sits just above the anchor line
# the moving groups: the left leg (leg + its boot), the right foot, and everything else (the upper body)
LEG_A = {"legs_back", "feet_back"}       # split below by x: after the mirror the left leg is x 12..14


def _move_group(layer, x):
    """Offset group of a pixel column of a leg/feet layer: the left leg (mirrored x 12..14) or the right foot."""
    return "a" if x >= 12 else "b"


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False, gear=None):
    """One frame as {layer: Canvas}: each layer's pixels moved by its group's whole-pixel offset. gear maps a slot to
    a recolour function (item tiers)."""
    offs = {"up": up, "a": a, "b": b}
    out = {}
    for k in LAYER_ORDER:
        src = PARTS[k]
        fn = (gear or {}).get(SLOT_OF.get(k, ""))
        c = Canvas(S, S)
        px = src.load()
        for y in range(src.height):
            for x in range(src.width):
                p = px[x, y]
                if not p[3]:
                    continue
                grp = _move_group(k, x) if k in LEG_A else "up"
                dx, dy = offs[grp]
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
    """The frame turned 90 degrees onto the ground (pixel exact), every layer by the same amount."""
    whole = flat(layers).img.rotate(90, expand=False)
    bbox = whole.getbbox()
    dy = FLOOR - bbox[3] if bbox else 0
    out = {}
    for k, c in layers.items():
        img = c.img.rotate(90, expand=False)
        n = Canvas(S, S)
        n.img.alpha_composite(img, (0, dy))
        out[k] = n
    return out


def anims(gear=None):
    f = lambda **kw: frame(gear=gear, **kw)  # noqa: E731
    idle = [f(), f(), f(up=(0, 1)), f(up=(0, 1))]
    # run: feet alternate (lift 1, step 1). The body never rises off the 3 px legs (that left a gap, user 2026-11-25):
    # it dips 1 px on the contact frames instead, overlapping the feet.
    run = [f(up=(0, 1), a=(1, 0), b=(-1, -1)), f(up=(0, 0), a=(1, 0), b=(0, -1)),
           f(up=(0, 0), a=(0, 0), b=(1, 0)), f(up=(0, 0), a=(-1, 0), b=(1, 0)),
           f(up=(0, 1), a=(-1, -1), b=(1, 0)), f(up=(0, 0), a=(0, -1), b=(1, 0)),
           f(up=(0, 0), a=(1, 0), b=(0, 0)), f(up=(0, 0), a=(1, 0), b=(-1, 0))]
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


# --- equipment tiers: the user's own layers recoloured with the item icons' material ramps (gear-icons PAL) -------
# user 2026-11-25: "dựa trên bản tôi vẽ phát triển các bậc khác". Shapes and pixels stay; colours follow the tier.
TIERS = {
    "iron": {"d": "#4a4f5c", "m": "#7a808c", "l": "#a8aeb8", "h": "#d7dce2", "t": "#7a808c", "T": "#4a4f5c",
             "b": "#6b4a2b", "B": "#4a321c", "g": "#8a3030", "G": "#c86a6a"},
    "steel": {"d": "#5f7186", "m": "#9fb3c8", "l": "#c9d6e2", "h": "#f2f7fb", "t": "#3f7fd0", "T": "#24508c",
              "b": "#5a3a26", "B": "#3e2819", "g": "#37b9e8", "G": "#bfe6ff"},
    "dragon": {"d": "#2e1b2e", "m": "#5a2f4f", "l": "#8a4a6e", "h": "#c27aa0", "t": "#c38df5", "T": "#7b4bb0",
               "b": "#3e2819", "B": "#2a1a10", "g": "#ff4a6a", "G": "#ffb3c0"},
    "aegis": {"d": "#8a5a1a", "m": "#d49a2a", "l": "#f2c14e", "h": "#fff2a8", "t": "#e8f0f6", "T": "#9fb3c8",
              "b": "#6b2a8a", "B": "#3e1a52", "g": "#4fd0ff", "G": "#d8f6ff"},
}
ITEMS = {"head": ["iron_cap", "steel_helm", "dragon_helm", "aegis_helm"],
         "chest": ["iron_chest", "steel_chest", "dragon_chest", "aegis_chest"],
         "legs": ["iron_greaves", "steel_greaves", "dragon_greaves", "aegis_greaves"],
         "arms": ["iron_gauntlets", "steel_gauntlets", "dragon_gauntlets", "aegis_gauntlets"],
         "feet": ["iron_boots", "steel_boots", "dragon_boots", "aegis_boots"],
         "weapon": ["iron_sword", "steel_sword", "dragon_blade", "aegis_blade"]}
TIER_ORDER = ["iron", "steel", "dragon", "aegis"]


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _scale(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c)


def recolour(tier, armour=False):
    """Colour map for one tier. armour=True (greaves, gauntlets, boots) turns every non-outline pixel to metal."""
    t = {k: _rgb(v) for k, v in TIERS[tier].items()}
    metal = [t["d"], t["m"], t["l"], t["h"]]

    def fn(p):
        r, g, b, a = p
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum < 40:                                     # the user's outline and darkest lines stay
            return p
        sat = max(r, g, b) - min(r, g, b)
        if armour:
            return (*metal[min(3, int(lum / 64))], a)
        if r > g + 60 and r > b + 60:                     # reds: plume, tunic, shield paint -> the tier accent
            k = 1.0 if lum >= 70 else (0.75 if lum >= 45 else 0.5)
            return (*_scale(t["g"], k), a)
        if r - b > 18 and lum > 120:                      # cream / gold: hilt, belt, trims -> the tier trim
            return (*(t["t"] if lum > 190 else t["T"]), a)
        if sat < 24:                                      # greys: helmet, blade, shield rim -> the metal ramp
            return (*metal[min(3, int((lum - 40) / 54))], a)
        if r > b:                                         # browns: grips, straps -> leather
            return (*(t["b"] if lum > 70 else t["B"]), a)
        return p

    return fn


def write_layers(here, anim_list, names, folder):
    folder.mkdir(parents=True, exist_ok=True)
    every = [fr for _, frames, *_ in anim_list for fr in frames]
    for k in names:
        strip([fr[k] for fr in every]).save(folder / f"{k}_strip.png")


if __name__ == "__main__":
    import json

    base = anims()
    flat_anims = [(n, [flat(fr) for fr in frames], fps, loop, extra) for n, frames, fps, loop, extra in base]
    check_connected(flat_anims, "knight")
    export(HERE, HERE.name, flat_anims, anchor=(24.0, float(FLOOR)), ground=True, body="idle")
    used = [k for k in LAYER_ORDER if any(fr[k].img.getbbox() for _, frames, *_ in base for fr in frames)]
    write_layers(HERE, base, used, HERE / "layers")
    meta_path = HERE / f"{HERE.name}.json"
    meta = json.loads(meta_path.read_text())
    meta["layers"] = used
    meta["outline"] = "none"          # the user's drawing has its own outline: the game must not add another
    meta["slots"] = {slot: [k for k, s in SLOT_OF.items() if s == slot and k in used] for slot in ITEMS}
    meta["base"] = ["body"]
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    for slot, items in ITEMS.items():
        layers = meta["slots"][slot]
        for tier, item in zip(TIER_ORDER, items):
            fn = recolour(tier, armour=slot in ("legs", "arms", "feet"))
            write_layers(HERE, anims({slot: fn}), layers, HERE / "gear" / item)
    print("OK", HERE.name, "layers", used, "+ 24 items")
