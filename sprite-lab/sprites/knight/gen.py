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


BARE_DY = 36          # the bare figure (rows 36..66 of the sheet) lines up with the armed one shifted up 36 rows


def _grey(rgb):
    r, g, b = rgb
    return max(r, g, b) - min(r, g, b) < 18 and max(r, g, b) > 60


def _armed_layer(x, y, rgb):
    """Gear layer of a pixel of the armed knight (left-facing crop); None for the face (the bare body keeps it)."""
    if 17 <= x <= 19 and y == 26:
        return "legs_back"
    if (17 <= x <= 19 and 27 <= y <= 28) or (24 <= x <= 25 and y == 28):
        return "feet_back"
    if (x <= 14 and y >= 14) or (x >= 23 and 20 <= y <= 27):
        return "weapon"                                   # the sword, and the shield (sword and board)
    if 15 <= x <= 16 and 21 <= y <= 24:
        return "arms_front"                               # the sword hand
    if 17 <= x <= 24 and 13 <= y <= 19 and not _grey(rgb):
        return None                                       # the face under the helmet
    if y <= 19:
        return "head"                                     # helmet and plume
    return "chest"


def _bare_layer(x, y, rgb):
    """Base layer of a pixel of the bare figure (user 2026-11-25: with the armour off the hero is this drawing)."""
    r, g, b = rgb
    if y == 26:
        return "legs_back"
    if y >= 27:
        return "feet_back"
    if y >= 19 and (x <= 16 or x >= 24):
        return "arms_front"                               # both arms hang at the sides
    if y >= 19:
        return "chest"
    skin = r > 190 and g > 120 and b < 190
    if skin or (18 <= x <= 23 and 14 <= y <= 18):
        return "body"                                     # face, eyes, mouth
    return "head"                                         # the black hair (a helmet replaces it)


def _split(box, dy, rule):
    im = Image.open(SRC).convert("RGBA")
    out = {k: Image.new("RGBA", (CROP[2], CROP[3])) for k in LAYER_ORDER}
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            p = im.getpixel((x, y))
            if not p[3]:
                continue
            k = rule(x, y - dy, p[:3])
            if k:
                out[k].putpixel((x, y - dy), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT              # face right like the other heroes; pixels unchanged
    return {k: v.transpose(flip) for k, v in out.items()}


def _parts():
    return _split((0, BARE_DY, 32, BARE_DY + 30), BARE_DY, _bare_layer)


ARMED = _split((0, 0, 32, 30), 0, _armed_layer)


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
        worn = (gear or {}).get(SLOT_OF.get(k, ""))
        fn, extra = worn if isinstance(worn, tuple) else (worn, [])
        src = ARMED[k].copy() if worn else PARTS[k]      # a worn slot shows the armed drawing's piece
        if worn and k == "head":
            for (ex, ey, col) in extra:                    # tier details on the helmet (horns, wings)
                src.putpixel((ex, ey), (*_rgb(col), 255))
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
    """The frame turned 90 degrees onto the ground (pixel exact), every layer by the same amount. The turn is done on
    an expanded canvas and the result is laid on the floor, centred on the anchor, so nothing is cut off (armed sets
    are wider: the old in-frame turn lost the body and legs)."""
    whole = flat(layers).img.rotate(90, expand=True)
    bbox = whole.getbbox()
    out = {}
    if not bbox:
        return layers
    w = bbox[2] - bbox[0]
    x0 = max(0, min(S - w, 24 - w // 2))
    y0 = FLOOR - (bbox[3] - bbox[1])
    for k, c in layers.items():
        img = c.img.rotate(90, expand=True).crop(bbox)
        n = Canvas(S, S)
        n.img.alpha_composite(img, (x0, y0))
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


# tier details added on the helmet, mirrored-crop coords (the helmet top is row 8-9, front x 15, back x 4-6); they
# touch the helmet outline so the figure stays one piece. user 2026-11-25: details are fine if the layout stays.
HELM_EXTRA = {
    "iron": [], "steel": [],
    "dragon": [(16, 11, "#7b4bb0"), (17, 10, "#c38df5"), (17, 9, "#08080c"), (18, 10, "#08080c"),
               (16, 10, "#08080c")],
    "aegis": [(4, 11, "#08080c"), (3, 10, "#e8f0f6"), (2, 9, "#ffffff"), (3, 11, "#c9d6e2"), (2, 10, "#e8f0f6"),
              (1, 9, "#08080c"), (1, 10, "#08080c"), (2, 11, "#08080c")],
}


def tier_fn(tier, slot):
    """iron keeps the user's own colours; the other tiers recolour (and the helmet gets its details)."""
    fn = (lambda p: p) if tier == "iron" else recolour(tier, armour=slot in ("legs", "arms", "feet"))
    return (fn, HELM_EXTRA[tier]) if slot == "head" else (fn, [])


def write_layers(here, anim_list, names, folder):
    folder.mkdir(parents=True, exist_ok=True)
    every = [fr for _, frames, *_ in anim_list for fr in frames]
    for k in names:
        strip([fr[k] for fr in every]).save(folder / f"{k}_strip.png")


# item icons (24 x 24) from the user's loose pieces on the sheet, scaled by whole numbers, coloured like the gear
PIECES = {"helmet": (36, 5, 52, 21), "shield": (55, 13, 63, 21), "legA": (67, 14, 70, 20), "legB": (73, 14, 76, 20),
          "sword": (37, 25, 57, 36), "tunic": (69, 26, 76, 35)}


def _piece(name, rows=None):
    im = Image.open(SRC).convert("RGBA").crop(PIECES[name])
    if rows:
        im = im.crop((0, rows[0], im.width, rows[1]))
    return im


def _icon_art(slot):
    """The slot's picture before colouring: a list of (image, x, y) on a 24 x 24 canvas."""
    up = lambda im, k: im.resize((im.width * k, im.height * k), Image.NEAREST)  # noqa: E731
    if slot == "head":
        h = _piece("helmet")
        return [(h, (24 - h.width) // 2, (24 - h.height) // 2)]
    if slot == "chest":
        t = up(_piece("tunic"), 2)
        return [(t, (24 - t.width) // 2, (24 - t.height) // 2)]
    if slot == "legs":
        a, b = up(_piece("legA"), 3), up(_piece("legB"), 3)
        return [(a, 3, 3), (b, 12, 3)]
    if slot == "feet":
        a, b = up(_piece("legA", (3, 6)), 3), up(_piece("legB", (3, 6)), 3)
        return [(a, 2, 7), (b, 13, 7)]
    if slot == "arms":
        hand = Image.open(SRC).convert("RGBA").crop((15, 21, 17, 25))
        g = up(hand, 4)
        return [(g, (24 - g.width) // 2, (24 - g.height) // 2)]
    sw, sh = _piece("sword"), _piece("shield")
    return [(sw, 1, 2), (sh, 15, 14)]


def write_icons(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            fn, _ = tier_fn(tier, slot)
            c = Image.new("RGBA", (24, 24))
            for im, x, y in _icon_art(slot):
                col = Image.new("RGBA", im.size)
                for yy in range(im.height):
                    for xx in range(im.width):
                        p = im.getpixel((xx, yy))
                        if p[3]:
                            col.putpixel((xx, yy), fn(p))
                c.alpha_composite(col, (x, y))
            c.save(folder / f"{item}.png")


if __name__ == "__main__":
    import json

    base = anims()
    flat_anims = [(n, [flat(fr) for fr in frames], fps, loop, extra) for n, frames, fps, loop, extra in base]
    check_connected(flat_anims, "knight")
    export(HERE, HERE.name, flat_anims, anchor=(24.0, float(FLOOR)), ground=True, body="idle")
    used = list(LAYER_ORDER)   # every layer, even one empty when bare (the weapon): worn items fill it
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
            write_layers(HERE, anims({slot: tier_fn(tier, slot)}), layers, HERE / "gear" / item)
    write_icons(HERE / "icons")
    print("OK", HERE.name, "layers", used, "+ 24 items + icons")
