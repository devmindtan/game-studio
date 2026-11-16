# game-studio: workspace làm game

Workspace gồm nhiều repo riêng. **Mỗi khi nhận yêu cầu, xác định loại yêu cầu theo bảng "Điều phối" bên dưới
rồi dùng đúng công cụ ghi trong đó.** Mọi thao tác máy móc đi qua `gamekit` (đã có sẵn trên PATH).

```text
game-studio/
├── CLAUDE.md, README.md          workflow này + hướng dẫn cho người
├── templates/
│   └── claude-code-game-studios/ framework gốc (49 agent, 74 skill), CHỈ ĐỌC. Mỗi game mới clone từ đây
├── games/
│   └── <slug>/                   mỗi game là một repo git riêng (clone template + Godot + addon gamekit)
└── tools/
    ├── gamekit/                  bộ công cụ của workspace: CLI, addon Godot, pipeline sprite, build/export
    └── lpc-generator/            Universal LPC Spritesheet Character Generator (clone upstream, CHỈ ĐỌC)
```

## Điều phối: yêu cầu → công cụ

Trước khi làm, xác định **game nào** (`gamekit list`). Nếu yêu cầu không nói rõ mà có nhiều game, hỏi lại.
Các lệnh `/skill` là skill của framework, nằm trong `games/<slug>/.claude/skills`. Hook và quyền của framework
chỉ được nạp khi Claude được mở **trong** `games/<slug>/`, nên việc thiết kế hay sản xuất kéo dài thì khuyên
người dùng mở phiên mới ở đó.

| Yêu cầu (ví dụ) | Công cụ / quy trình |
|---|---|
| "Làm game mới", "tôi có ý tưởng…" | `gamekit new <slug> "Tên"` → trong `games/<slug>`: `/prototype` (đã mô tả được game), `/start` (còn mơ hồ), `/brainstorm` (chưa có ý tưởng) |
| "Thêm/sửa tính năng" (nhỏ, rõ) | sửa code trong `src/` → `gamekit test <g>` → `gamekit shot <g>` để nhìn kết quả |
| "Thêm tính năng" (lớn, nhiều hệ thống) | `/quick-design` (thay đổi nhỏ) hoặc `/design-system` → `/create-stories` → `/dev-story` → `/story-done` |
| "Game khó/dễ quá", "chỉnh tốc độ…" | sửa `assets/data/*.json` (không hardcode trong code) → `/balance-check` → `gamekit test` + `gamekit shot` |
| "Thêm nhân vật", "sprite người/quái dạng người" | `gamekit lpc` (người dùng phối đồ, xuất **ZIP split animations**) → chép vào `games/<g>/assets/source/lpc/<tên>.zip` → `gamekit sprites <g>` → `gamekit preview <g> <tên>` → dùng `LpcCharacter` trong code |
| Art khác (tile, cảnh, hiệu ứng, icon) | kit chưa có công cụ. Định hướng bằng `/art-bible`, `/asset-spec`; tạm thời vẽ bằng code (`_draw`) như game đom đóm |
| Menu, HUD, giao diện | `/ux-design` → `/team-ui`; bắt buộc chụp màn hình bằng `gamekit shot` |
| Âm thanh | `/team-audio` (kit chưa có công cụ âm thanh) |
| "Game bị lỗi…" | `/bug-report` → viết test hồi quy, **chạy cho thấy test fail trước** → sửa → `gamekit test` |
| "Review code" | `/code-review` của game (bản scoped `games/<g>`), không dùng bản chung |
| "Chơi thử / chạy xem" | `gamekit run <g>` (người chơi), `gamekit shot <g> [scene] [frames] [-- args]` (Claude tự nhìn) |
| "Giờ làm gì tiếp?", "dự án tới đâu rồi?" | `/next-step`, `/project-stage-detect` |
| "Xuất game", "build", "phát hành" | tăng `config/version` trong `project.godot` → `gamekit export <g>` → `gamekit smoke-web <g>` → `/release-checklist`, `/patch-notes` |
| "Cập nhật framework" | `gamekit update-template`; với từng game, làm theo `UPGRADING.md` của template |
| Thư mục game lẫn file của framework (README/CHANGELOG/.github của tool) | `gamekit tidy <g>` (gamekit new đã tự chạy) |
| "Sửa/mở rộng bộ công cụ" | sửa `tools/gamekit` → tăng `tools/gamekit/VERSION` → `gamekit install <g>` cho mỗi game → `gamekit test <g>` |
| Máy mới, lệnh lỗi, thiếu phần mềm | `gamekit doctor` |

## Quy tắc chung

- **Nhìn tận mắt rồi mới báo xong.** Thay đổi nào người chơi thấy được thì phải chạy game và xem ảnh
  (`gamekit shot`); ảnh dùng làm bằng chứng lưu ở `games/<g>/production/qa/evidence/`. Parse được code
  chưa có nghĩa là game chạy được.
- **Test fail thì không export.** `gamekit export` tự chặn; không dùng `SKIP_TESTS=1` để lách.
- **Credit LPC là bắt buộc** (CC-BY-SA / GPL / OGA-BY). `gamekit sprites` dừng nếu thiếu credit; game nào
  dùng nhân vật LPC thì phải có màn hình Credits đọc từ `assets/credits/`.
- **Giữ 10% tài nguyên máy** (quy tắc chung của máy này): `gamekit` tự chạy Godot, Chrome và export qua
  `limited`. Mỗi lúc chỉ một việc nặng; xóa file tạm sau khi xong.
- **Không sửa** `templates/` và `tools/lpc-generator/` (cả hai là clone upstream). Muốn tùy biến thì sửa ở
  `games/<g>` hoặc `tools/gamekit`.
- **Addon `games/<g>/addons/gamekit/` là bản sao.** Sửa ở `tools/gamekit/addon/` rồi chạy `gamekit install`.
- **Git có ba tầng:** repo gốc `game-studio/` chỉ quản lý `CLAUDE.md`, `README.md` và `tools/gamekit`. Mỗi game là
  một repo riêng: remote `framework` trỏ về upstream của framework, còn `origin` để dành cho repo riêng của game.
  `templates/` và `tools/lpc-generator/` là clone upstream. Chỉ commit khi người dùng yêu cầu.
- **README của game nói về game** (cách chơi, phím, cấu trúc, ai sở hữu thư mục nào). Tài liệu về công cụ
  nằm ở `tools/gamekit/README.md` và trong template, không chép vào game.
- API Godot 4.7: tra `games/<g>/docs/engine-reference/godot/` trước khi dùng API mà mình không chắc.
