"""sheet: write a multi-animation sprite the Sprite Lab way, from a gen.py.

    from sheet import export
    export(HERE, "slime", [("move", frames, 8, True, {}), ...], anchor=(12, 23), ground=True)

Writes <name>_strip.png, <name>.png (first frame), preview.png (one row per
animation, no grid), <animation>.gif and <name>.json (write_anim_meta, which
also runs the ground check when ground=True). Extras per animation: any of
"durations_ms", "airborne".
"""
from __future__ import annotations

from pathlib import Path

from spritekit import Canvas, gif, preview, strip, write_anim_meta


def export(here: Path, name: str, animations, anchor, ground=False, preview_scale=None, gif_scale=None):
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop, **extra}
                     for n, f, fps, loop, extra in animations],
                    anchor=anchor, ground=ground)
    return here / f"{name}_strip.png"
