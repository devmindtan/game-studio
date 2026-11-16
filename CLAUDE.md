# game-studio: workspace làm game

Workspace gồm nhiều repo riêng. **Mỗi khi nhận yêu cầu, xác định loại yêu cầu theo bảng "Điều phối" bên dưới
rồi dùng đúng công cụ ghi trong đó.** Mọi thao tác máy móc đi qua `gamekit` (đã có sẵn trên PATH).

```text
game-studio/
├── CLAUDE.md, README.md          workflow này + hướng dẫn cho người
├── .opencode/skills/             skill cho agent làm việc trong workspace (pixel-sprite, …)
├── templates/
│   └── claude-code-game-studios/ framework gốc (49 agent, 74 skill), CHỈ ĐỌC. Mỗi game mới clone từ đây
├── games/
│   └── <slug>/                   mỗi game là một repo git riêng (clone template + Godot + addon gamekit)
└── tools/
    ├── gamekit/                  bộ công cụ của workspace: CLI, addon Godot, pipeline sprite, build/export
    └── lpc-generator/            Universal LPC Spritesheet Character Generator (clone upstream, CHỈ ĐỌC)
```

## Điều phối: yêu cầu → công cụ

**Mọi dòng trong bảng đều kết thúc bằng: kiểm tra → commit** theo mục "Quy tắc commit" ở cuối file.
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
| Art khác (tile, cảnh, hiệu ứng, icon, sprite không LPC) | `gamekit art new <g> <tên> [--size N]` → sửa `assets/source/sprites/<tên>/gen.py` → `gamekit art run <g> <tên>` → xem `preview.png`/`anim.gif` → `gamekit shot <g>` để kiểm tra trong game; hướng nghệ thuật bằng `/art-bible`, `/asset-spec`; skill `.opencode/skills/pixel-sprite` |
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
  `templates/` và `tools/lpc-generator/` là clone upstream. Commit theo mục "Quy tắc commit" bên dưới.
- **README của game nói về game** (cách chơi, phím, cấu trúc, ai sở hữu thư mục nào). Tài liệu về công cụ
  nằm ở `tools/gamekit/README.md` và trong template, không chép vào game.
- API Godot 4.7: tra `games/<g>/docs/engine-reference/godot/` trước khi dùng API mà mình không chắc.

## Quy tắc commit (bắt buộc, chỉ thị cố định của người dùng từ 2026-11-16)

**Mỗi lần chỉnh sửa đều phải commit, ngay trong lượt làm việc đó.** Không kết thúc lượt nào khi còn thay đổi
chưa commit. Chỉ thị này đã là "user instruction" mà mục "No commits without user instruction" của framework
yêu cầu, nên không cần hỏi lại trước mỗi commit.

### 1. Commit vào repo nào

| File đã sửa | Repo | Ghi chú |
|---|---|---|
| `games/<g>/**` | repo của game đó (`git -C games/<g>`) | |
| `CLAUDE.md`, `README.md`, `.gitignore`, `.opencode/**`, `tools/gamekit/**` | repo gốc `game-studio/` | |
| `templates/**`, `tools/lpc-generator/**` | **không bao giờ** | clone upstream, chỉ đọc. Lỡ sửa thì `git checkout -- .` để hoàn tác |

Thay đổi trải trên nhiều repo thì **mỗi repo một commit**. Ví dụ sửa gamekit:
1. Commit ở repo gốc: `feat(gamekit): …` và tăng `tools/gamekit/VERSION`.
2. `gamekit install <g>` rồi commit ở từng game: `chore(gamekit): update addon to <version>`.

### 2. Trước khi commit (kiểm tra theo loại thay đổi)

| Đã đổi | Phải chạy và đạt |
|---|---|
| code / data của game | `gamekit test <g>` → `N passed, 0 failed` |
| thứ người chơi nhìn thấy (hình, UI, cảm giác chơi) | thêm `gamekit shot <g> …` và **xem ảnh**; ảnh bằng chứng lưu vào `production/qa/evidence/<việc>/` và commit kèm |
| `assets/data/*.json` | test như trên (hook commit của framework chặn JSON lỗi) |
| sprite LPC | `gamekit sprites <g>` thành công (có credit) + `gamekit test <g>` |
| script trong `tools/gamekit` | `bash -n` (shell) / `python3 -m py_compile` (python); `gamekit install` + `gamekit test` trên ít nhất một game |
| cấu hình export | `gamekit export <g> <preset>` cho preset bị đổi |
| chỉ tài liệu | đọc lại các đường dẫn và lệnh được nhắc tới, xem chúng còn đúng không |

Kiểm tra fail thì **không commit trạng thái hỏng**: sửa cho đạt, hoặc báo lại cho người dùng. Chỉ khi người
dùng bảo commit dở dang thì mới commit, và dùng type `wip`.

### 3. Stage

- Chạy `git status --short` trước, đọc từng dòng. Stage **đúng các file của thay đổi này** bằng đường dẫn cụ thể
  (`git add <paths>`). Chỉ dùng `git add -A` khi `status` cho thấy mọi thứ đều thuộc thay đổi này.
- Commit kèm file `.uid` mà Godot sinh ra cạnh script/shader (quy tắc của framework); **không** commit `.godot/`,
  `builds/`, file tạm, log, `*.import` của file bị xóa, hay credential/khóa ký.
- **Có** commit: `export_presets.cfg`, `assets/source/lpc/*.zip`, ảnh trong `production/qa/evidence/`.

### 4. Chia commit

- Một commit = một thay đổi logic, có thể revert riêng. Việc không liên quan nhau thì tách commit.
- Thứ tự khi một việc có nhiều bước: setup/cấu hình → code + test → tài liệu.

### 5. Message (Conventional Commits, tiếng Anh: skill `/write-changelog` và `/patch-notes` đọc message)

```text
<type>(<scope>): <subject: imperative, ≤ 72 ký tự, không chấm cuối>

<body: LÀM GÌ và VÌ SAO; chi tiết quan trọng mà diff không nói lên>

Verified: <lệnh đã chạy và kết quả, ví dụ "gamekit test: 16 passed, 0 failed; shot: evidence/rain-tuning/01.png">
Design: <design/game-brief.md | design/gdd/<x>.md | Story: <ID>>     (với thay đổi gameplay)

Co-Authored-By: <attribution theo system prompt của phiên>
```

- `type`: `feat` (tính năng), `fix` (sửa lỗi), `refactor`, `perf`, `test`, `docs`, `build` (export/đóng gói),
  `chore` (cấu hình, công cụ, cập nhật addon), `wip` (chỉ khi người dùng yêu cầu).
- `scope`: hệ thống bị đổi, ví dụ `core`, `game`, `hud`, `balance`, `sprites`, `export`, `gamekit`, `workspace`.
- Sửa lỗi thì body ghi nguyên nhân, và ghi rằng test hồi quy đã **fail trước khi sửa** rồi pass sau khi sửa.

### 6. Sau khi commit

- `git log --oneline -1` để xác nhận; báo cho người dùng **hash và subject** của từng commit (ghi rõ repo nào).
- **Không push** trừ khi người dùng yêu cầu. Không `--amend` commit đã push, không `--force`, không `--no-verify`
  (hook của framework là lớp bảo vệ, không được lách).
- Hook commit của game chỉ nạp khi Claude được mở trong `games/<g>/`. Commit từ repo gốc vẫn phải tự
  tuân thủ các mục kiểm tra ở trên.
