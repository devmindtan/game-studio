# Art references

Free references used as **idea sources** when designing sprites, effects, UI icons.
Nothing here is shipped as artwork in the game; games draw their own art in Sprite Lab
using these as mood/style direction (composition, palette, shape language, timing).

## Palettes (`palettes/`)
Fetched from the public Lospec API (`lospec.com/palette-list/<slug>.json`).
Each palette belongs to its listed author; do not add license text without the author's terms.

| id | name | author | colors |
|---|---|---|---|
| afr-32 | AFR-32 | Alpha6 | 32 |
| aragon16 | Aragon16 | Space-AgeWrangler | 16 |
| astria-solseturs | Ástríða sólseturs | joe70098 | 9 |
| blue-glass | BLUE GLASS | Eliimperio | 8 |
| brazilian-afternoon | brazilian afternoon | Ju | 42 |
| castern | Castern | Snowy Owl | 14 |
| cc-29 | CC-29 | Alpha6 | 29 |
| coldfire-gb | Coldfire GB | Kerrie Lake | 4 |
| comfy52 | comfy52 | bess | 52 |
| dawn-32 | DawnBringer 32 | (unspecified) | 32 |
| dead-ice | dead ice | polyphrog | 4 |
| foxfire | Foxfire | Lotaru | 4 |
| frozen-fire | Frozen Fire | Cool Beans | 14 |
| greyt-bit | Greyt-bit | skeddles | 8 |
| hilda32 | Hilda32 | skeddles | 32 |
| icywitch | IcyWitch | Naym | 6 |
| magicolor-16 | magicolor 16 | polyphrog | 16 |
| mushroom | Mushroom | Jimison3 | 14 |
| pola5 | POLA5 | |NOXITIVE| | 5 |
| resurrect-64 | Resurrect 64 | Kerrie Lake | 64 |
| st-8-phoenix | ST 8 Phoenix | Skiller Thomson | 8 |
| summers-past-16 | Summers Past-16 | keidding | 16 |
| sunfall | sunfall | sunfall | 10 |
| sunraze | Sunraze | Dain Kaplan | 14 |
| verdant-valley | verdant valley | polyphrog | 24 |
| wheat-field | Wheat Field | bess | 10 |
| winter-wonderland | Winter Wonderland | Jimison3 | 8 |

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
