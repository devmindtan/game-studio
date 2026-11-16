# gamekit

Bộ công cụ dùng chung cho mọi game trong `game-studio/games/`. Một lệnh duy nhất: `gamekit` (có link trong
`~/.local/bin`). `gamekit help` liệt kê tất cả các lệnh.

```text
tools/gamekit/
├── bin/gamekit                 CLI
├── VERSION                     phiên bản kit (được ghi vào addons/gamekit/VERSION của mỗi game)
├── addon/gamekit/              addon Godot, được CHÉP vào <game>/addons/gamekit bằng `gamekit install`
│   ├── lpc/lpc_character.gd        class LpcCharacter: phát animation theo hành động + hướng (có trong bản export)
│   ├── lpc/lpc_layout.json         bố cục sheet LPC (lấy từ constants.ts của generator) + fps/loop
│   ├── lpc/build_sprite_frames.gd  PNG → SpriteFrames (.tres)                  (không vào bản export)
│   ├── debug/character_viewer.*    màn xem nhân vật                            (không vào bản export)
│   └── test/run_tests.gd           bộ chạy test headless, fail nếu có test không load được (không vào bản export)
├── pipeline/
│   ├── lpc_ingest.py               ZIP/PNG từ generator → assets/sprites/characters + credit gộp
│   ├── lpc_sample_compose.py       ghép nhân vật mẫu offline từ tools/lpc-generator
│   └── spritekit.py                helper Pillow cho pixel art agent tự vẽ
├── build/
│   ├── install_export_templates.sh tải template export (kiểm tra checksum, chỉ giữ Linux/Windows/Web)
│   ├── export.sh                   import → test → export → zip
│   └── smoke_web.sh + web_smoke_cdp.mjs   mở bản Web trong Chrome headless, in console, chụp ảnh
└── templates/                  project.godot, export_presets.cfg, Makefile cho game mới
    └── sprite/gen.py           mẫu generator cho `gamekit art new`
```

## Cấu hình cho mọi AI agent

`gamekit agents-link` (và `gamekit doctor`, qua `--check`) giữ một bản gốc duy nhất cho mỗi thứ:

| Thứ | Bản gốc | Link cho từng agent |
|---|---|---|
| Hướng dẫn workspace | `AGENTS.md` | `CLAUDE.md` = `@AGENTS.md`; `GEMINI.md` → `AGENTS.md`; Aider: `.aider.conf.yml` |
| Skill workspace | `.agents/skills/<tên>/` | `.claude/skills/<tên>` → `../../.agents/skills/<tên>` (OpenCode và Codex đọc `.agents/skills`) |
| Hướng dẫn trong game | `games/<g>/AGENTS.md` (từ `templates/AGENTS.game.md`) | `GEMINI.md` → `AGENTS.md` |
| Skill framework trong game | `games/<g>/.claude/skills/` | `.agents/skills` → `../.claude/skills` |

`gamekit tidy` và `gamekit new` tự tạo phần của game.

## Tách game khỏi công cụ

`gamekit new` clone template, sau đó tự chạy `gamekit tidy`. Lệnh này đưa các file thuộc về repo framework ra khỏi game
(`README.md` → README riêng của game, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `UPGRADING.md`, `.github/`,
`studio-tests/`, tài liệu hướng dẫn framework trong `docs/`), chuyển `LICENSE` (MIT) vào `LICENSES/`, và đổi remote
`origin` thành `framework`. Bản gốc của các file này vẫn còn trong `templates/claude-code-game-studios/`.
Những gì framework cần để chạy (`.claude/`, `CLAUDE.md`, `project.yaml`, `docs/engine-reference`, …) được giữ lại.

## Cấu trúc một game do gamekit tạo

```text
games/<slug>/
├── project.godot, export_presets.cfg, Makefile (gọi gamekit)
├── src/                       code game (core = luật chơi thuần, test được; game = scene)
├── assets/data/*.json         số liệu cân bằng
├── assets/source/lpc/         ← thả file ZIP/PNG xuất từ generator (Godot bỏ qua, không vào bản build)
├── assets/source/sprites/     ← generator + preview + .ase của pixel art tự vẽ (Godot bỏ qua)
├── assets/sprites/characters/<tên>/   pipeline sinh ra: standard/*.png, <tên>_frames.tres, credits.csv
├── assets/sprites/custom/<tên>/       PNG cho Godot do `gamekit art` sinh ra
├── assets/credits/            CREDITS.md + lpc_credits.csv (có trong bản build)
├── addons/gamekit/            bản sao addon (không sửa ở đây)
├── tests/unit, tests/integration
└── builds/                    kết quả export (git bỏ qua)
```

## Nhân vật LPC

1. `gamekit lpc`: mở http://localhost:5173 (lần đầu sẽ chạy `npm ci`). Phối đồ cho nhân vật, chọn
   **Download → ZIP "split animations"** (gói này có sẵn credit và `character.json`).
2. Đổi tên file thành tên nhân vật (`knight.zip`), chép vào `games/<g>/assets/source/lpc/`.
   Nếu chỉ có PNG cả sheet: `knight.png` + `knight.credits.csv` (+ `knight.json` nếu có).
3. `gamekit sprites <g>`: tạo `knight_frames.tres` (animation `walk_down`, `slash_left`, `hurt`, …).
   Lệnh này **dừng với lỗi khi thiếu credit**.
4. `gamekit preview <g> knight`: xem 4 hướng; phím mũi tên đi, Shift chạy, J/K/L/U/H để thử các đòn.
5. Trong code:

   ```gdscript
   var hero := LpcCharacter.new()
   hero.sprite_frames = load("res://assets/sprites/characters/knight/knight_frames.tres")
   add_child(hero)
   hero.face(velocity)                                # mỗi frame
   hero.play_action(&"walk" if velocity else &"idle")
   ```

Tốc độ và chế độ lặp của từng animation nằm trong `addon/gamekit/lpc/lpc_layout.json`. Sửa xong thì chạy
`gamekit install <g>` rồi `gamekit sprites <g>`. Animation cỡ lớn (128/192px, thư mục `custom/`) hiện mới
được chép sang, chưa chuyển thành SpriteFrames.

## Pixel art tự vẽ (agent)

Dùng cho tile, icon, hiệu ứng, quái, nhân vật không theo LPC. Agent viết generator Python (Pillow), render
ra PNG, tự xem preview rồi sửa; LibreSprite chỉ dùng để người chỉnh tay và chuyển `.ase`.

```bash
gamekit art new <game> light-mote --size 24   # tạo assets/source/sprites/light-mote/gen.py
gamekit art run <game> light-mote             # chạy gen.py -> PNG + preview.png + anim.gif
gamekit art ase <game> light-mote             # PNG -> .ase trong assets/source/
gamekit art open <game> light-mote            # mở .ase bằng LibreSprite
```

- File sinh ra:
  - `assets/sprites/custom/<tên>/<tên>.png` và `<tên>_strip.png` — Godot import.
  - `assets/source/sprites/<tên>/` — `gen.py`, `preview.png`, `anim.gif`, `<tên>.ase`; Godot bỏ qua.
- `gen.py` import helper `pipeline/spritekit.py` (ASCII map, outline, strip, grid, GIF, preview, `.ase`).
  Sửa `gen.py`, không sửa helper trong game.
- Preview là ảnh phóng to nearest có lưới, để agent đọc bằng công cụ đọc ảnh của nó. `anim.gif` để xem chuyển động.
- `gamekit doctor` kiểm tra `libresprite`. Bản 1.3 không có MCP; xem `.agents/skills/pixel-sprite/SKILL.md`
  để biết giới hạn và quy trình đầy đủ.

## Xuất game

```bash
gamekit templates                 # một lần cho mỗi phiên bản Godot
gamekit export <g>                # test → Linux + Windows + Web → builds/dist/<slug>-<version>-<platform>.zip
gamekit export <g> Web            # một nền tảng
DEBUG=1 gamekit export <g>        # bản debug
gamekit smoke-web <g>             # bản Web có tải và chạy được không (Chrome headless)
```

- Phiên bản lấy từ `config/version` trong `project.godot`.
- Bản Web dùng biến thể no-threads, upload thẳng file zip lên itch.io được.
- Bản export loại bỏ `tests/`, `addons/gamekit/{test,debug}`, builder sprite, cùng mọi thư mục có `.gdignore`
  (`.claude`, `docs`, `design`, `production`, `studio-tests`, `assets/source`).

## Sửa bộ công cụ

Sửa trong `tools/gamekit/`, tăng `VERSION`, rồi `gamekit install <g>` cho từng game. `gamekit list` cho biết
mỗi game đang dùng phiên bản kit nào. Lệnh `install` không ghi đè `export_presets.cfg` và `Makefile` đã có,
để giữ các tùy chỉnh riêng của từng game.
