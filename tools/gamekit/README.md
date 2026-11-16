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
    └── sprite/gen.py           mẫu generator (nhiều animation) cho `gamekit art new`
```

## Cấu hình cho mọi AI agent

`gamekit agents-link` (và `gamekit doctor`, qua `--check`) giữ một bản gốc duy nhất cho mỗi thứ:

| Thứ | Bản gốc | Link cho từng agent |
|---|---|---|
| Hướng dẫn workspace | `AGENTS.md` | `CLAUDE.md` = `@AGENTS.md`; Aider: `.aider.conf.yml` |
| Skill workspace | `.agents/skills/<tên>/` | `.claude/skills/<tên>` → `../../.agents/skills/<tên>` (OpenCode và Codex đọc `.agents/skills`) |
| Hướng dẫn trong game | `games/<g>/AGENTS.md` (từ `templates/AGENTS.game.md`) | agent đọc trực tiếp |
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
├── assets/sprites/characters/<tên>/   pipeline sinh ra: standard/*.png, <tên>_frames.tres, credits.csv
├── assets/sprites/custom/<tên>/       sprite đã promote từ Sprite Lab (strip + json)
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

## Pixel art: Sprite Lab

Mọi sprite pixel art được làm và thử trong `sprite-lab/` (project Godot riêng), không làm trong game. Quy
trình đầy đủ ở [`sprite-lab/README.md`](../../sprite-lab/README.md) và skill `pixel-sprite`.

```bash
gamekit art new <tên> [--size N]      # sprite-lab/sprites/<tên>/gen.py (mẫu nhiều animation)
gamekit art rig new <tên> [hero|hero-sword|knight] # pose rig Pixelbolt có thể sửa
gamekit art rig validate <tên>        # kiểm tra pose source
gamekit art rig inspect <tên> [anim]  # onion skin + diagnostics
gamekit art rig motion <tên> <anim> [px/s] # xem tiếp đất, trượt chân, loop, quỹ đạo (mặc định 24)
gamekit art rig build <tên>            # xuất Pixelbolt thành strip/metadata Sprite Lab
gamekit art run <tên>                 # vẽ + kiểm tra <tên>.json (frames, animation, điểm neo)
gamekit art shot <tên> sheet|move     # ảnh để xem: mọi animation / 8 khoảnh khắc thử di chuyển
gamekit art lab [<tên>] [sheet|move]  # mở lab (người dùng tự điều khiển)
gamekit art test | check | list       # test lab / kiểm mọi sprite / sprite nào ở game nào
gamekit art promote <tên> <game>      # chép strip + json (+ "source") vào game
gamekit art ase|open <tên>            # .ase cho LibreSprite
```

- `gamekit art new <game> …` bị từ chối: sprite không được tạo trong game (bài học 2026-11-16).
- Nhân vật dùng pose/bone và attachment có thể bắt đầu bằng `gamekit art rig new`; nguồn `<tên>.poses.json`
  được Pixelbolt 0.17.0 compile và import lại thành strip Sprite Lab. Pixelbolt lưu thời lượng từng frame;
  `SpriteSheet` giữ nguyên timing này qua `durations_ms`. Package cục bộ được ghim trong `tools/gamekit/package-lock.json`;
  cài bằng `npm ci --prefix tools/gamekit` (Node.js 20+). `gen.py` vẫn phù hợp với sprite vẽ theo pixel/tọa độ.
- Addon `addons/gamekit/sprites/`: `SpriteSheet` (đọc json, chọn frame theo animation và thời gian, vẽ)
  , `SpriteAnchor` (đặt theo điểm neo, kể cả khi lật) và `SpriteHitbox` (vùng trúng của hiệu ứng, đặt cùng neo
  và tỉ lệ với hình vẽ). Dùng chung cho lab và mọi game.
- `spritekit.py`: `from_rows`, `outline`, `strip`, `preview`, `gif`, `write_meta` / `write_anim_meta`
  (`ground=True` + `check_ground`: nhân vật phải chạm đất ở mọi frame không `airborne`;
  `"hitbox"` của animation được `fit_hitbox` đo từ pixel, `check_hitbox` từ chối hitbox lệch; `body=` đo thân
  bằng `fit_body`, `check_body` kiểm tra; `gamekit test` nạp mọi script trong `src/` nên lỗi parse là FAIL)
  (ghi `<tên>.json`), `check_meta`, `.ase` qua LibreSprite.
- Export preset gói `assets/sprites/*.json` để game đọc được metadata.

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
