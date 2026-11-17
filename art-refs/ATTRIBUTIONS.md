# Art references

Free references used as **idea sources** when designing sprites, effects, UI icons.
Nothing here is shipped as artwork in the game; games draw their own art in Sprite Lab
using these as mood/style direction (composition, palette, shape language, timing).

## Palettes (`palettes/`)
Fetched from the public Lospec API (`lospec.com/palette-list/<slug>.json`).
Each palette belongs to its listed author; do not add license text without the author's terms.

| id | name | author | colors |
|---|---|---|---|
| dawn-32 | DawnBringer 32 | (unspecified) | 32 |
| cc-29 | CC-29 | Alpha6 | 29 |
| magicolor-16 | magicolor 16 | polyphrog | 16 |
| resurrect-64 | Resurrect 64 | Kerrie Lake | 64 |
| greyt-bit | Greyt-bit | skeddles | 8 |

Reference-only use: share composition notes, do not re-export palette JSON publicly as your own branding.

## LPC sheets (`tools/lpc-generator/spritesheets/`)
The workspace already ships the Universal LPC Spritesheet Character Generator (MIT) with its
`CREDITS.csv`; the sprites there are OGA-BY / CC-BY-SA / GPL. Use them to study how professionals
layer an LPC character, not as copy-paste assets: **all LPC art used in the game needs credit**
(see `gamekit sprites` — it stops when credit is missing).

## External links (not vendored)
- Kenney assets (CC0): https://kenney.nl/ — free for commercial use; good for particles/explosion style reference, not for guessing frame layout (we draw our own in `gen.py`).
- OpenGameArt (OGA): mostly credits-required (CC-BY-SA / OGA-BY / GPL); prefer for study, not for quick fetch.
- Lospec gallery examples: palette-specific examples by community members; always read the footnote on the palette page before reusing an example pixel pattern.

## Rule of thumb
- Read, then draw your own. If an asset helped your design, record the URL and the author in the asset's `source`/credits if shipped.
