"""sheet: write a multi-animation sprite the Sprite Lab way, from a gen.py.

    from sheet import export
    export(HERE, "slime", [("move", frames, 8, True, {}), ...], anchor=(12, 23), ground=True)

Writes <name>_strip.png, <name>.png (first frame), preview.png (one row per
animation, no grid), <animation>.gif and <name>.json (write_anim_meta, which
also runs the ground check when ground=True). Extras per animation: any of
"durations_ms", "airborne", "hitbox". body="<animation>" stores the body circle
measured from that animation (spritekit.fit_body).
"""
from __future__ import annotations

from pathlib import Path

import json

from spritekit import Canvas, check_layers, gif, preview, strip, write_anim_meta


CREATURE_MIN = {"move": 6, "attack": 6, "hurt": 3, "death": 6}
UPPER_CHANGE_MOVE = 0.04
UPPER_CHANGE_WINDUP = 0.08


def _upper_change(a, b, upper=0.6):
    """Share of opaque pixels that differ between frames a and b in the top `upper` of their joint bbox."""
    boxes = [x for x in (a.img.getbbox(), b.img.getbbox()) if x]
    if not boxes:
        return 0.0
    top = min(x[1] for x in boxes)
    bottom = max(x[3] for x in boxes)
    cut = top + (bottom - top) * upper
    pa, pb = a.img.load(), b.img.load()
    diff = solid = 0
    for y in range(top, int(cut)):
        for x in range(a.width):
            ca, cb = pa[x, y], pb[x, y]
            if ca[3] or cb[3]:
                solid += 1
                if ca != cb:
                    diff += 1
    return diff / solid if solid else 0.0


def check_creature(here: Path, animations):
    """creature-v1 (sprite-lab/CREATURE_STANDARD.md): a sprite with brief.json must have every required
    animation with enough frames, one description per frame, and a body that moves (not only the legs).
    Returns a list of problems (empty = fine)."""
    import json
    bp = here / "brief.json"
    if not bp.exists():
        return []
    brief = json.loads(bp.read_text())
    if brief.get("standard") != "creature-v1":
        return []
    anims = {n: frames for n, frames, _, _, _ in animations}
    desc = brief.get("frames", {})
    need = dict(CREATURE_MIN)
    if "jump" in anims or "crouch" in anims:
        need.update({"crouch": 2, "jump": 4})
    problems = []
    for n, k in need.items():
        if n not in anims:
            problems.append(f"{n}: missing (creature-v1 needs {', '.join(need)})")
            continue
        if len(anims[n]) < k:
            problems.append(f"{n}: {len(anims[n])} frames, creature-v1 needs >= {k}")
    for n, frames in anims.items():
        d = desc.get(n)
        if d is None or len(d) != len(frames):
            problems.append(f"{n}: brief.json describes {0 if d is None else len(d)} frames, the sprite has {len(frames)}")
    mv = anims.get("move", [])
    for i in range(len(mv)):
        ch = _upper_change(mv[i], mv[(i + 1) % len(mv)])
        if ch < UPPER_CHANGE_MOVE:
            problems.append(f"move {i}->{(i + 1) % len(mv)}: upper body changes {ch:.1%} (< {UPPER_CHANGE_MOVE:.0%}): only the legs move")
    if mv and anims.get("attack"):
        ch = _upper_change(mv[0], anims["attack"][0])
        if ch < UPPER_CHANGE_WINDUP:
            problems.append(f"attack 0: wind-up pose differs {ch:.1%} from move 0 (< {UPPER_CHANGE_WINDUP:.0%}): no real pose change")
    return problems


def export(here: Path, name: str, animations, anchor, ground=False, preview_scale=None, gif_scale=None, body=None):
    problems = check_creature(here, animations)
    if problems:
        raise ValueError("creature-v1 (sprite-lab/CREATURE_STANDARD.md): " + "; ".join(problems))
    flat = [f for _, frames, _, _, _ in animations for f in frames]
    w, h = flat[0].width, flat[0].height
    strip(flat).save(here / f"{name}_strip.png")
    flat[0].save(here / f"{name}.png")
    cols = max(len(frames) for _, frames, _, _, _ in animations)
    sheet = Canvas(cols * w, len(animations) * h)
    for row, (_, frames, _, _, _) in enumerate(animations):
        sheet.paste(strip(frames), 0, row * h)
    zoom = preview_scale or max(2, 192 // max(w, h))
    preview([sheet], here / "preview.png", scale=zoom, grid_lines=False)
    for anim, frames, fps, _, _ in animations:
        gif(frames, here / f"{anim}.gif", fps=fps, scale=gif_scale or max(1, 96 // max(w, h)))
    write_anim_meta(here / f"{name}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop, **extra,
                      **({"hit_mask": f.hit_masks} if getattr(f, "hit_masks", None) else {})}
                     for n, f, fps, loop, extra in animations],
                    anchor=anchor, ground=ground, body=body)
    return here / f"{name}_strip.png"


def export_layered(here: Path, name: str, animations, anchor, outline, ground=False, body=None,
                   preview_scale=None, gif_scale=None):
    """Like export(), for a character drawn in layers (minifig.draw_layers).

    animations: (name, [dict layer -> Canvas per frame], fps, loop, extra).
    Writes the composed + outlined sprite exactly as export() does, plus
    layers/<layer>_strip.png (no outline) for every layer used in any frame, and
    adds "layers" (z order) and "outline" to <name>.json. check_layers verifies
    that composing the layers gives the strip pixel for pixel; equipment replaces
    layers and the game composes them the same way."""
    import minifig as mf

    def outlined(layers):
        c = mf.compose(layers)
        c.outline(outline)
        return c

    flat_anims = [(n, [outlined(f) for f in frames], fps, loop, extra) for n, frames, fps, loop, extra in animations]
    export(here, name, flat_anims, anchor, ground=ground, preview_scale=preview_scale, gif_scale=gif_scale, body=body)
    every = [f for _, frames, _, _, _ in animations for f in frames]
    order = list(every[0].keys())
    used = [k for k in order if any(f[k].img.getbbox() for f in every)]
    layer_dir = here / "layers"
    layer_dir.mkdir(exist_ok=True)
    for old in layer_dir.glob("*_strip.png*"):   # strips of layers no longer used, and their .import
        if old.name.split("_strip.png")[0] not in used:
            old.unlink()
    for k in used:
        strip([f[k] for f in every]).save(layer_dir / f"{k}_strip.png")

    # review sheet: the first frame split by equipment slot (left to right), then composed
    first = every[0]
    w0, h0 = first[used[0]].width, first[used[0]].height
    groups = [[k for k in parts if k in used] for parts in mf.SLOTS.values()]
    groups = [g for g in groups if g]
    exploded = Canvas((len(groups) + 1) * (w0 + 4), h0)
    for i, parts in enumerate(groups):
        exploded.paste(mf.compose([first[k] for k in parts]), i * (w0 + 4), 0)
    exploded.paste(outlined(first), len(groups) * (w0 + 4), 0)
    preview([exploded], here / "layers.png", scale=preview_scale or 4, grid_lines=False)
    meta_path = here / f"{name}.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["layers"] = used
    meta["outline"] = outline
    # equipment slots -> their layers (only layers this sprite uses); the base is not a slot
    meta["slots"] = {slot: [k for k in parts if k in used] for slot, parts in mf.SLOTS.items()
                     if any(k in used for k in parts)}
    meta["base"] = [k for k in mf.BASE if k in used]
    from PIL import Image
    problems = check_layers(meta, Image.open(here / f"{name}_strip.png"), layer_dir)
    if problems:
        raise ValueError("; ".join(problems))
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return here / f"{name}_strip.png"
