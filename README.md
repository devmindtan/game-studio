# game-studio

Workspace làm game 2D bằng Godot 4.7, dùng được với mọi AI agent: Claude Code, OpenCode, Codex,
Cursor, Aider…

| Thư mục / file | Là gì |
|---|---|
| `games/<slug>/` | Mỗi game là một repo riêng: framework Claude Code Game Studios + Godot + addon gamekit |
| `AGENTS.md` | **Workflow cho mọi agent** (bản gốc duy nhất). `CLAUDE.md` import nó |
| `LESSONS.md` | Lỗi đã gặp và chỗ đã chặn chúng. Mỗi lần sai, agent sửa rule/công cụ và ghi thêm một dòng |
| `.agents/skills/` | Skill dùng chung (ví dụ `pixel-sprite`). `.claude/skills/` chỉ chứa symlink trỏ về đây |
| `templates/claude-code-game-studios/` | Bản gốc của framework để tạo game mới (không sửa trực tiếp) |
| `tools/gamekit/` | Bộ công cụ: CLI `gamekit`, pipeline sprite LPC, pixel art, build/export. Xem [README](tools/gamekit/README.md) |
| `tools/lpc-generator/` | Bộ tạo nhân vật LPC (web app) |

Game hiện có: **dom-dom-dem-mua** (Đom Đóm Đêm Mưa).

## Bắt đầu nhanh

```bash
gamekit doctor                          # kiểm tra máy đã đủ công cụ chưa (và link của agent)
gamekit list                            # danh sách game

gamekit new space-miner "Space Miner"   # tạo game mới
cd games/space-miner                    # mở agent ở đây (claude / opencode / codex …) rồi /prototype hoặc /start

gamekit run dom-dom-dem-mua             # chơi
gamekit test dom-dom-dem-mua            # chạy test
gamekit export dom-dom-dem-mua          # build Linux + Windows + Web → games/<g>/builds/dist/
```

Trong một thư mục game có thể bỏ tên game (`gamekit test`) hoặc dùng `make help`.

## Ra yêu cầu cho agent

Cứ nói yêu cầu bằng lời thường. [AGENTS.md](AGENTS.md) có bảng điều phối, để agent tự chọn công cụ phù hợp.
Ví dụ:

- "Làm cho tôi game bắn thiên thạch": `gamekit new` rồi `/prototype`.
- "Thêm nhân vật hiệp sĩ vào game": dùng bộ tạo LPC rồi `gamekit sprites`.
- "Vẽ icon/hiệu ứng/quái pixel art": skill `pixel-sprite`, tức `gamekit art new <g> <tên>`, sửa `gen.py`,
  rồi `gamekit art run <g> <tên>`. Agent viết code Python vẽ từng pixel và tự xem ảnh preview.
- "Game khó quá": chỉnh `assets/data/*.json`, rồi test và chụp màn hình.
- "Xuất bản web để đưa lên itch.io": `gamekit export <g> Web` rồi `gamekit smoke-web`.

Muốn làm việc sâu với một game (thiết kế, sprint, review), nên mở agent **ngay trong** `games/<slug>/`.
Với Claude Code, hook và quy tắc của framework chỉ có hiệu lực khi mở ở đó.

## Thêm skill hoặc sửa hướng dẫn cho agent

- Hướng dẫn: sửa `AGENTS.md`. Không viết vào `CLAUDE.md`.
- Skill mới: tạo `.agents/skills/<tên>/SKILL.md`, rồi chạy `gamekit agents-link`.
- Kiểm tra: `gamekit doctor` (hoặc `gamekit agents-link --check`).
