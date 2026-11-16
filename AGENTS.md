# game-studio: workspace làm game

> **Bản gốc duy nhất cho mọi AI agent** (Claude Code, OpenCode, Codex, Cursor, Aider…).
> `CLAUDE.md` chỉ import file này. Muốn sửa workflow thì sửa **ở đây**.

Workspace gồm nhiều repo riêng. **Mỗi khi nhận yêu cầu, xác định loại yêu cầu theo bảng "Điều phối" bên dưới
rồi dùng đúng công cụ ghi trong đó.** Mọi thao tác máy móc đi qua `gamekit` (đã có sẵn trên PATH).

```text
game-studio/
├── AGENTS.md                     workflow này (bản gốc); CLAUDE.md trỏ về đây
├── README.md                     hướng dẫn cho người
├── LESSONS.md                    lỗi đã gặp → chỗ đã chặn (đọc trước khi làm việc cùng loại)
├── .agents/skills/<tên>/SKILL.md skill dùng chung (bản gốc), ví dụ pixel-sprite
├── .claude/skills/<tên>          symlink → .agents/skills/<tên> (do `gamekit agents-link` tạo)
├── sprite-lab/                   Sprite Lab: project Godot để làm + thử MỌI sprite (sheet, di chuyển), rồi promote vào game
├── templates/
│   └── claude-code-game-studios/ framework gốc (49 agent, 74 skill), CHỈ ĐỌC. Mỗi game mới clone từ đây
├── games/
│   └── <slug>/                   mỗi game là một repo git riêng (clone template + Godot + addon gamekit)
└── tools/
    ├── gamekit/                  bộ công cụ của workspace: CLI, addon Godot, pipeline sprite, pixel art, build/export
    └── lpc-generator/            Universal LPC Spritesheet Character Generator (clone upstream, CHỈ ĐỌC)
```

## Agent nào đọc gì

| Agent | Hướng dẫn | Skill |
|---|---|---|
| Codex, OpenCode, Cursor | `AGENTS.md` | `.agents/skills/` (OpenCode đọc thêm `.claude/skills/`) |
| Claude Code | `CLAUDE.md` → `@AGENTS.md` | `.claude/skills/` (symlink tới `.agents/skills/`) |
| Aider | `.aider.conf.yml` nạp `AGENTS.md` ở chế độ chỉ đọc | như trên |

- **Thêm skill mới:** tạo `.agents/skills/<tên>/SKILL.md` (frontmatter có `name`, `description`), rồi chạy
  `gamekit agents-link`. Không tạo skill riêng cho từng agent, không sửa các symlink bằng tay.
- **Trong từng game** (`games/<g>/`): `AGENTS.md` của game trỏ tới `CLAUDE.md` của framework;
  `.agents/skills` là symlink tới `.claude/skills` (74 skill của framework). Các skill này viết cho Claude Code
  (hook, hỏi người dùng, subagent). Agent khác vẫn đọc làm theo được, nhưng phải tự làm phần mà công cụ của
  Claude Code lo, ví dụ tự chạy kiểm tra mà hook vẫn chạy.
- Skill có ghi tên công cụ (`Read`, `Bash`…) thì hiểu là công cụ tương đương của agent đang dùng.
- `gamekit doctor` báo khi symlink thiếu hoặc hỏng.

## Điều phối: yêu cầu → công cụ

**Mọi dòng trong bảng đều kết thúc bằng: kiểm tra → commit** theo mục "Quy tắc commit" ở cuối file.
Trước khi làm, xác định **game nào** (`gamekit list`). Nếu yêu cầu không nói rõ mà có nhiều game, hỏi lại.
Các lệnh `/skill` là skill của framework, nằm trong `games/<slug>/.claude/skills/<tên>/SKILL.md`. Với Claude Code,
hook và quyền của framework chỉ được nạp khi agent được mở **trong** `games/<slug>/`, nên việc thiết kế hay sản
xuất kéo dài thì khuyên người dùng mở phiên mới ở đó.

| Yêu cầu (ví dụ) | Công cụ / quy trình |
|---|---|
| "Làm game mới", "tôi có ý tưởng…" | `gamekit new <slug> "Tên"` → trong `games/<slug>`: `/prototype` (đã mô tả được game), `/start` (còn mơ hồ), `/brainstorm` (chưa có ý tưởng) |
| "Thêm/sửa tính năng" (nhỏ, rõ) | sửa code trong `src/` → `gamekit test <g>` → `gamekit shot <g>` để nhìn kết quả |
| "Thêm tính năng" (lớn, nhiều hệ thống) | `/quick-design` (thay đổi nhỏ) hoặc `/design-system` → `/create-stories` → `/dev-story` → `/story-done` |
| "Game khó/dễ quá", "chỉnh tốc độ…" | sửa `assets/data/*.json` (không hardcode trong code) → `/balance-check` → `gamekit test` + `gamekit shot` |
| "Thêm nhân vật", "sprite người/quái dạng người" | `gamekit lpc` (người dùng phối đồ, xuất **ZIP split animations**) → chép vào `games/<g>/assets/source/lpc/<tên>.zip` → `gamekit sprites <g>` → `gamekit preview <g> <tên>` → dùng `LpcCharacter` trong code |
| Sprite / art pixel (nhân vật, quái, icon, hiệu ứng, tile; không phải LPC), thử animation, thử di chuyển | skill **`.agents/skills/pixel-sprite/SKILL.md`**, làm trong **Sprite Lab** (`sprite-lab/`, không bao giờ trong game): `gamekit art new <tên>` → sửa `gen.py` → `gamekit art run <tên>` → xem `preview.png` → `gamekit art shot <tên> sheet` + `… move` → `gamekit art test` → commit repo gốc → khi game cần: `gamekit art promote <tên> <g>`; hướng nghệ thuật bằng `/art-bible`, `/asset-spec` |
| Menu, HUD, giao diện | `/ux-design` → `/team-ui`; bắt buộc chụp màn hình bằng `gamekit shot` |
| Âm thanh | `/team-audio` (kit chưa có công cụ âm thanh) |
| "Game bị lỗi…" | `/bug-report` → viết test hồi quy, **chạy cho thấy test fail trước** → sửa → `gamekit test` |
| "Review code" | `/code-review` của game (bản scoped `games/<g>`), không dùng bản chung |
| "Chơi thử / chạy xem" | `gamekit run <g>` (người chơi), `gamekit shot <g> [scene] [frames] [-- args]` (agent tự nhìn) |
| "Giờ làm gì tiếp?", "dự án tới đâu rồi?" | `/next-step`, `/project-stage-detect` |
| "Xuất game", "build", "phát hành" | tăng `config/version` trong `project.godot` → `gamekit export <g>` → `gamekit smoke-web <g>` → `/release-checklist`, `/patch-notes` |
| "Cập nhật framework" | `gamekit update-template`; với từng game, làm theo `UPGRADING.md` của template |
| Thư mục game lẫn file của framework (README/CHANGELOG/.github của tool) | `gamekit tidy <g>` (gamekit new đã tự chạy) |
| "Thêm/sửa skill hoặc cấu hình agent" | sửa `.agents/skills/` hoặc `AGENTS.md` → `gamekit agents-link` → `gamekit doctor` |
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
- **Git có ba tầng:** repo gốc `game-studio/` quản lý `AGENTS.md`, `LESSONS.md`, `CLAUDE.md`, `README.md`, `.agents/`,
  `.claude/skills/` (symlink), `.aider.conf.yml`, `sprite-lab/` và `tools/gamekit`. Mỗi game là một repo riêng: remote `framework`
  trỏ về upstream của framework, còn `origin` để dành cho repo riêng của game. `templates/` và
  `tools/lpc-generator/` là clone upstream. Commit theo mục "Quy tắc commit" bên dưới.
- **README của game nói về game** (cách chơi, phím, cấu trúc, ai sở hữu thư mục nào). Tài liệu về công cụ
  nằm ở `tools/gamekit/README.md` và trong template, không chép vào game.
- API Godot 4.7: tra `games/<g>/docs/engine-reference/godot/` trước khi dùng API mà mình không chắc.
- **Shell là zsh.** Không dựa vào word splitting (`set -- $s`, `for x in $list` với chuỗi có dấu cách): gọi
  từng lệnh riêng hoặc dùng mảng. **Không gom nhiều đường dẫn vào một biến** (`L="a b"; git add $L` hỏng):
  viết thẳng các đường dẫn vào lệnh. Script trong `tools/gamekit` viết bằng bash (`#!/usr/bin/env bash`).
- **Sprite đặt theo điểm neo, không theo tâm canvas.** Sprite nào cũng có `<tên>.json` (do `gen.py` gọi
  `write_meta`) và game vẽ qua `SpriteAnchor`. Chi tiết trong skill `pixel-sprite`.

## Sai một lần → sửa rule (bắt buộc, chỉ thị của người dùng từ 2026-11-16)

Mỗi khi agent làm sai, hoặc người dùng chỉ ra lỗi, thì **sửa lỗi chưa phải là xong**. Trong cùng lượt đó:

1. **Tìm nguyên nhân gốc**, không chỉ triệu chứng ("sprite lệch" → "code căn theo tâm canvas, số liệu gõ tay").
2. **Chặn ở tầng mạnh nhất có thể**, theo thứ tự ưu tiên:
   1. công cụ tự từ chối (`gamekit`, script báo lỗi và exit khác 0);
   2. test tự động (cho thấy **test fail trước khi sửa**);
   3. rule trong skill liên quan (`.agents/skills/<tên>/SKILL.md`) hoặc trong `AGENTS.md`;
   4. chỉ ghi chú, khi ba cách trên không làm được.
3. **Ghi một dòng vào `LESSONS.md`**: ngày, triệu chứng → nguyên nhân gốc, chặn bằng gì.
4. **Commit** phần sửa rule cùng lúc với phần sửa lỗi (rule ở repo gốc, code ở repo game: mỗi repo một commit).

Trước khi làm một việc, đọc các dòng liên quan trong `LESSONS.md` để không lặp lại lỗi cũ.

## Quy tắc commit (bắt buộc, chỉ thị cố định của người dùng từ 2026-11-16)

**Mỗi lần chỉnh sửa đều phải commit, ngay trong lượt làm việc đó.** Không kết thúc lượt nào khi còn thay đổi
chưa commit. Chỉ thị này đã là "user instruction" mà mục "No commits without user instruction" của framework
yêu cầu, nên không cần hỏi lại trước mỗi commit. Áp dụng cho **mọi agent**.

### 1. Commit vào repo nào

| File đã sửa | Repo | Ghi chú |
|---|---|---|
| `games/<g>/**` | repo của game đó (`git -C games/<g>`) | |
| `AGENTS.md`, `LESSONS.md`, `CLAUDE.md`, `README.md`, `.gitignore`, `.aider.conf.yml`, `.agents/**`, `.claude/skills/**`, `sprite-lab/**`, `tools/gamekit/**` | repo gốc `game-studio/` | |
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
| sprite pixel art (lab) | `gamekit art run <tên>` + **xem** `preview.png`, ảnh `art shot … sheet` và `… move`; `gamekit art test` |
| sprite đã promote vào game | `gamekit test <g>` + `gamekit shot <g>` và xem ảnh |
| script trong `tools/gamekit` | `bash -n` (shell) / `python3 -m py_compile` (python); `gamekit install` + `gamekit test` trên ít nhất một game |
| skill hoặc cấu hình agent | `gamekit agents-link` + `gamekit doctor` không còn mục `MISS` |
| cấu hình export | `gamekit export <g> <preset>` cho preset bị đổi |
| chỉ tài liệu | đọc lại các đường dẫn và lệnh được nhắc tới, xem chúng còn đúng không |

Kiểm tra fail thì **không commit trạng thái hỏng**: sửa cho đạt, hoặc báo lại cho người dùng. Chỉ khi người
dùng bảo commit dở dang thì mới commit, và dùng type `wip`.

### 3. Stage

- Chạy `git status --short` trước, đọc từng dòng. Stage **đúng các file của thay đổi này** bằng đường dẫn cụ thể
  (`git add <paths>`). Chỉ dùng `git add -A` khi `status` cho thấy mọi thứ đều thuộc thay đổi này.
- **Commit kèm đường dẫn:** `git commit -F - -- <các đường dẫn của thay đổi này>`. Với đường dẫn, Git chỉ
  commit đúng các file đó; thứ khác đang staged (một `git mv`/`git rm` từ trước) không lọt vào được.
- **Xem stage ở một lệnh riêng**, đọc xong mới commit: `git diff --cached --stat -M` không được nối `&&`
  với `git commit` (nối thì không kịp đọc). Một lệnh commit lỗi thì dừng, kiểm tra index rồi mới làm tiếp.
- Sửa `.gitignore`: pattern chỉ dành cho thư mục gốc phải có `/` đầu (`/templates/`), rồi chạy `git status`
  xem có file nào vừa biến mất khỏi danh sách.
- Commit kèm file `.uid` mà Godot sinh ra cạnh script/shader (quy tắc của framework); **không** commit `.godot/`,
  `builds/`, file tạm, log, `*.import` của file bị xóa, hay credential/khóa ký.
- **Có** commit: `export_presets.cfg`, `assets/source/lpc/*.zip`, `sprite-lab/sprites/<tên>/` (gen.py, strip, json, preview),
  ảnh trong `production/qa/evidence/`.

### 4. Chia commit

- Một commit = một thay đổi logic, có thể revert riêng. Việc không liên quan nhau thì tách commit.
- Thứ tự khi một việc có nhiều bước: setup/cấu hình → code + test → tài liệu.

### 5. Message (Conventional Commits, tiếng Anh: skill `/write-changelog` và `/patch-notes` đọc message)

```text
<type>(<scope>): <subject: imperative, ≤ 72 ký tự, không chấm cuối>

<body: LÀM GÌ và VÌ SAO; chi tiết quan trọng mà diff không nói lên>

Verified: <lệnh đã chạy và kết quả, ví dụ "gamekit test: 16 passed, 0 failed; shot: evidence/rain-tuning/01.png">
Design: <design/game-brief.md | design/gdd/<x>.md | Story: <ID>>     (với thay đổi gameplay)

<dòng ghi công cho agent theo quy ước của agent đó, ví dụ Co-Authored-By>
```

- `type`: `feat` (tính năng), `fix` (sửa lỗi), `refactor`, `perf`, `test`, `docs`, `build` (export/đóng gói),
  `chore` (cấu hình, công cụ, cập nhật addon), `wip` (chỉ khi người dùng yêu cầu).
- `scope`: hệ thống bị đổi, ví dụ `core`, `game`, `hud`, `balance`, `sprites`, `art`, `export`, `gamekit`, `agents`, `workspace`.
- Sửa lỗi thì body ghi nguyên nhân, và ghi rằng test hồi quy đã **fail trước khi sửa** rồi pass sau khi sửa.

### 6. Sau khi commit

- `git log --oneline -1` để xác nhận; báo cho người dùng **hash và subject** của từng commit (ghi rõ repo nào).
- **Không push** trừ khi người dùng yêu cầu. Không `--amend` commit đã push, không `--force`, không `--no-verify`
  (hook của framework là lớp bảo vệ, không được lách).
- Hook commit của game chỉ chạy với Claude Code mở trong `games/<g>/`. Agent khác, hoặc commit từ repo gốc,
  vẫn phải tự tuân thủ các mục kiểm tra ở trên.
