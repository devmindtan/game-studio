"""userart: helpers for animating the user's own character drawings (sprite-lab/sources/user/, user 2026-11-25:
the agent only animates and edits the user's art).

check_connected(anims, name): refuses an export where a frame's opaque pixels are not one 8-connected piece, e.g. the
body lifted off short legs (2026-11-25, the knight's run). Call it in gen.py before export().
"""

from __future__ import annotations


def check_connected(anims, name: str) -> None:
    bad = []
    for anim_name, frames, *_ in anims:
        for i, c in enumerate(frames):
            px = c.img.load()
            w, h = c.img.size
            pts = {(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0}
            if not pts:
                continue
            seen = set()
            todo = [next(iter(pts))]
            while todo:
                q = todo.pop()
                if q in seen:
                    continue
                seen.add(q)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (q[0] + dx, q[1] + dy)
                        if n in pts and n not in seen:
                            todo.append(n)
            if len(seen) != len(pts):
                bad.append(f"{anim_name} {i}")
    if bad:
        raise SystemExit(f"{name}: parts come apart in " + ", ".join(bad))
