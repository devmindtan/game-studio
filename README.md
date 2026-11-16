# game-studio

Workspace làm game 2D bằng Godot 4.7, kết hợp với Claude Code.

| Thư mục | Là gì |
|---|---|
| `games/<slug>/` | Mỗi game là một repo riêng: framework Claude Code Game Studios + Godot + addon gamekit |
| `.opencode/skills/` | Skill cho agent trong workspace (ví dụ `pixel-sprite`) |
| `templates/claude-code-game-studios/` | Bản gốc của framework để tạo game mới (không sửa trực tiếp) |
| `tools/gamekit/` | Bộ công cụ: CLI `gamekit`, pipeline sprite LPC, pixel art, build/export. Xem [README](tools/gamekit/README.md) |
| `tools/lpc-generator/` | Bộ tạo nhân vật LPC (web app) |

Game hiện có: **dom-dom-dem-mua** (Đom Đóm Đêm Mưa).

## Bắt đầu nhanh

```bash
gamekit doctor                          # kiểm tra máy đã đủ công cụ chưa
gamekit list                            # danh sách game

gamekit new space-miner "Space Miner"   # tạo game mới
cd games/space-miner && claude          # mở Claude trong game rồi gõ /prototype hoặc /start

gamekit run dom-dom-dem-mua             # chơi
gamekit test dom-dom-dem-mua            # chạy test
gamekit export dom-dom-dem-mua          # build Linux + Windows + Web → games/<g>/builds/dist/
```

Trong một thư mục game có thể bỏ tên game (`gamekit test`) hoặc dùng `make help`.

## Ra yêu cầu cho Claude

Cứ nói yêu cầu bằng lời thường. [CLAUDE.md](CLAUDE.md) có bảng điều phối, để Claude tự chọn công cụ phù hợp.
Ví dụ:

- "Làm cho tôi game bắn thiên thạch": `gamekit new` rồi `/prototype`.
- "Thêm nhân vật hiệp sĩ vào game": dùng bộ tạo LPC rồi `gamekit sprites`.
- "Vẽ icon/hiệu ứng/quái pixel art": `gamekit art new <g> <tên>` rồi sửa `gen.py`, `gamekit art run <g> <tên>`; agent tự xem preview.
- "Game khó quá": chỉnh `assets/data/*.json`, rồi test và chụp màn hình.
- "Xuất bản web để đưa lên itch.io": `gamekit export <g> Web` rồi `gamekit smoke-web`.

Muốn làm việc sâu với một game (thiết kế, sprint, review), nên mở Claude **ngay trong** `games/<slug>/`.
Khi đó hook và các quy tắc của framework mới có hiệu lực.
