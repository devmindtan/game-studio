#!/usr/bin/env python3
"""Generator "hero-gear": the 48 equipment items drawn ON the heroes (swordsman, mage).

For every item (gear-icons ITEMS: class x slot x rarity) the hero is re-drawn with that item's
look, using the hero's own poses (its gen.py), and only the layers of the item's slot are
written: sprite-lab/sprites/<hero>/gear/<item>/<layer>_strip.png (no outline; same frame order
as <hero>_strip.png). The game swaps those layers in with SpriteSheet.compose_layers, so a worn
item shows on the hero in the lobby, the equipment screen and the run.

Looks follow the icons (same material ramps, gear-icons PAL): knight iron / steel / dragon /
aegis, mage cloth / arcane / void / star. Shapes: knight helmet (crest, horns, wings by
rarity) instead of hair, plate pauldron on the chest, metal gauntlet hands, longer and brighter
blade; mage hat / robe / trousers / sleeves / shoes / staff orb recoloured per rarity.
review.png: per class, one row per rarity (whole set worn), idle + run frames, x4.
Chạy: python3 sprite-lab/sprites/hero-gear/gen.py   (gamekit art run hero-gear)
"""

import copy
import importlib.util
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


HERE = Path(__file__).resolve().parent
SPRITES = HERE.parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(SPRITES.parent / "lib"))

from PIL import Image  # noqa: E402
import minifig as mf  # noqa: E402
from minifig import put, rect  # noqa: E402
from spritekit import Canvas, strip  # noqa: E402

RARITIES = ["common", "rare", "epic", "legendary"]
SLOT_ORDER = ["head", "chest", "legs", "arms", "feet", "weapon"]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ICONS = _load("gear_icons_gen", SPRITES / "gear-icons" / "gen.py")
HEROES = {"knight": "swordsman", "mage": "mage"}


# --- knight looks -----------------------------------------------------------------

def knight_helm(P, rarity):
    """A closed great helm over the whole head (user 2026-11-21: the old cap only sat on top, the face
    and sides showed): dome, cheek plates, neck guard, a face plate with one dark eye slit."""
    def draw(c, p, g):
        hx, hy = g["head"]
        rect(c, hx - 3, hy - 10, hx + 2, hy - 10, P["m"])        # dome top
        rect(c, hx - 4, hy - 9, hx + 4, hy, P["m"])             # the shell: covers the whole face block
        rect(c, hx - 4, hy - 9, hx - 3, hy, P["d"])             # back of the head in shade
        put(c, hx - 1, hy - 9, P["h"])                          # highlight on the dome
        put(c, hx, hy - 9, P["l"])
        put(c, hx - 2, hy - 8, P["l"])
        rect(c, hx - 4, hy - 6, hx + 4, hy - 6, P["t"])         # brow band
        rect(c, hx, hy - 4, hx + 4, hy - 4, "#14111c")          # eye slit
        put(c, hx + 2, hy - 4, P["h"] if p.get("eyes") not in ("closed", "x") else "#14111c")   # eye glint
        rect(c, hx + 1, hy - 3, hx + 4, hy - 1, P["l"])         # face plate, lit side
        put(c, hx + 3, hy - 2, P["d"])                          # breathing holes
        put(c, hx + 3, hy, P["d"])
        rect(c, hx - 4, hy, hx + 4, hy, P["d"])                 # lower rim
        if rarity == "rare":                                    # crest
            rect(c, hx - 2, hy - 11, hx + 1, hy - 11, P["t"])
        if rarity == "epic":                                    # horns
            for x, y in ((-4, -11), (-5, -12), (2, -11), (3, -12)):
                put(c, hx + x, hy + y, P["n"])
        if rarity == "legendary":                               # wings + gem
            for x, y, k in ((-5, -9, "w"), (-6, -10, "w"), (-7, -11, "w"), (-6, -9, "W"), (-5, -8, "W")):
                put(c, hx + x, hy + y, P[k])
            put(c, hx, hy - 6, P["g"])
    return draw


def knight_neck(base_neck, P, rarity):
    """Scarf knot (the hero's mark) plus a shoulder plate, by rarity a spike or a gem."""
    def draw(c, p, g):
        base_neck(c, p, g)
        sx, sy = g["sh_front"]
        rect(c, sx - 2, sy - 1, sx + 1, sy, P["l"])
        put(c, sx + 1, sy, P["d"])
        put(c, sx - 2, sy - 1, P["h"])
        if rarity in ("epic", "legendary"):
            put(c, sx - 1, sy - 2, P["n"] if rarity == "epic" else P["w"])
        if rarity == "legendary":
            t = g["top"]
            put(c, t[0], t[1] + 4, P["g"])
    return draw


def knight_look(mod, slot, P, rarity):
    pal = mod.PAL
    if slot == "head":
        mod.CHAR["hair"] = knight_helm(P, rarity)
    elif slot == "chest":
        pal.update(tunic=P["m"], tunic_l=P["l"], tunic_d=P["d"], belt=P["b"], buckle=P["t"] if rarity != "common" else P["l"])
        mod.CHAR["neck"] = knight_neck(mod.neck, P, rarity)
    elif slot == "legs":
        pal.update(pants=P["m"], pants_d=P["d"])
    elif slot == "arms":
        pal.update(sleeve=P["m"], sleeve_d=P["d"], skin=P["l"], skin_d=P["m"])   # gauntlet hands
    elif slot == "feet":
        pal.update(boot=P["l"] if rarity == "legendary" else P["m"], boot_d=P["d"])
    elif slot == "weapon":
        pal.update(blade=P["h"] if rarity != "epic" else P["l"], blade_d=P["m"] if rarity != "common" else P["d"],
                   guard=P["t"] if rarity != "common" else P["m"], grip=P["b"])
        mod.BLADE = {"common": 9, "rare": 10, "epic": 11, "legendary": 12}[rarity]


# --- mage looks ---------------------------------------------------------------------

def mage_look(mod, slot, P, rarity):
    pal = mod.PAL
    if slot == "head":
        pal.update(hat=P["m"], hat_d=P["d"], hat_l=P["l"], gold=P["t"] if rarity != "common" else P["l"],
                   gold_d=P["T"] if rarity != "common" else P["d"])
        if rarity in ("epic", "legendary"):
            pal["gold"] = P["g"] if rarity == "epic" else P["t"]
    elif slot == "chest":
        pal.update(robe=P["m"], robe_d=P["d"], robe_l=P["l"], trim=P["t"] if rarity != "common" else P["c"],
                   belt=P["T"] if rarity != "common" else P["b"])
    elif slot == "legs":
        pal.update(pants=P["m"], pants_d=P["d"])
    elif slot == "arms":
        pal.update(sleeve=P["m"], sleeve_d=P["d"])
    elif slot == "feet":
        pal.update(boot=P["l"] if rarity == "legendary" else P["m"], boot_d=P["d"])
    elif slot == "weapon":
        pal.update(wood=P["b"], wood_d=P["B"], magic=P["G"], magic_mid=P["g"], core="#ffffff")
        if rarity == "common":
            pal.update(magic_deep=P["g"])


LOOKS = {"knight": knight_look, "mage": mage_look}


# --- rendering ------------------------------------------------------------------------

def frames(mod):
    """Layers of every frame, in the hero's strip order (ANIMATIONS)."""
    out = []
    for anim, fr, _, _, _ in mod.ANIMATIONS:
        fn = getattr(mod, anim)
        out += [fn(i) for i in range(len(fr))]
    return out


def render_item(cls, slot, rarity):
    mod = HERO_MODS[cls]
    saved = (copy.deepcopy(mod.PAL), dict(mod.CHAR), getattr(mod, "BLADE", None))
    P = dict(ICONS.PAL[cls][rarity])
    for role, fb in {"n": "h", "N": "l", "w": "h", "W": "l", "c": "l", "C": "m", "b": "d", "B": "d"}.items():
        P.setdefault(role, P[fb])
    try:
        LOOKS[cls](mod, slot, P, rarity)
        mod.CHAR["pal"] = mod.PAL
        layers = frames(mod)
    finally:
        mod.PAL.clear()
        mod.PAL.update(saved[0])
        mod.CHAR.clear()
        mod.CHAR.update(saved[1])
        if saved[2] is not None:
            mod.BLADE = saved[2]
    return layers


def write_item(cls, slot, item, layers):
    out = SPRITES / HEROES[cls] / "gear" / item
    out.mkdir(parents=True, exist_ok=True)
    for name in mf.SLOTS[slot]:
        strip([f[name] for f in layers]).save(out / f"{name}_strip.png")


def review(path, sets):
    """Per class and rarity: the hero wearing the whole set, idle 0 and run 2, x4."""
    z = 4
    tiles = []
    for cls in ["knight", "mage"]:
        base = frames(HERO_MODS[cls])
        for rarity in RARITIES:
            row = []
            for fi in (0, 6):
                L = dict(base[fi])
                for slot in SLOT_ORDER:
                    for name in mf.SLOTS[slot]:
                        L[name] = sets[(cls, slot, rarity)][fi][name]
                c = mf.compose([L[n] for n in mf.LAYERS])
                c.outline(mf.OUTLINE)
                row.append(c.img.resize((mf.W * z, mf.H * z), Image.NEAREST))
            tiles.append(row)
    img = Image.new("RGBA", (2 * mf.W * z, len(tiles) * mf.H * z), (36, 34, 48, 255))
    for r, row in enumerate(tiles):
        for k, t in enumerate(row):
            img.alpha_composite(t, (k * mf.W * z, r * mf.H * z))
    img.save(path)


HERO_MODS = {cls: _load(f"{hero}_gen", SPRITES / hero / "gen.py") for cls, hero in HEROES.items()}

if __name__ == "__main__":
    sets = {}
    for (cls, slot), ids in ICONS.ITEMS.items():
        for k, rarity in enumerate(RARITIES):
            layers = render_item(cls, slot, rarity)
            write_item(cls, slot, ids[k], layers)
            sets[(cls, slot, rarity)] = layers
    review(HERE / "review.png", sets)
    print("OK hero-gear: %d items" % len(sets))
