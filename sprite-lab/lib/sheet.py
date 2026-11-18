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


def export(here: Path, name: str, animations, anchor, ground=False, preview_scale=None, gif_scale=None, body=None):
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
