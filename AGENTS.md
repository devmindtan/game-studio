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
├── design-web/                   Design Lab: dựng màn hình game trên web (1280×720, bàn phím) trước khi vào Godot
├── templates/
│   └── claude-code-game-studios/ framework gốc (49 agent, 74 skill), CHỈ ĐỌC. Mỗi game mới clone từ đây
├── games/
│   └── <slug>/                   mỗi game là một repo git riêng (clone template + Godot + addon gamekit)
└── tools/
    ├── gamekit/                  bộ công cụ của workspace: CLI, addon Godot, pipeline sprite, pixel art, build/export
    ├── gdgraph/                  index GDScript cho graphify (graphify không đọc .gd)
    ├── gpuhost/                  kết nối máy GPU desktop-kndgm60 qua SSH tunnel để chạy ComfyUI/art nặng
    ├── craft-anything/           (tùy chọn) lò prototype vứt đi: dựng project mới từ mô tả, tự build + self-test + ảnh
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
| Mọi việc lớn/nhiều bước | chia thành task **nguyên tử** trước khi code: skill **`.agents/skills/free-agent-workloop/SKILL.md`** — mỗi task một thay đổi, tự kiểm tra và commit được, làm xong một cái mới sang cái kế tiếp; khi tắc/không xem được ảnh thì dừng và báo rõ |
| Sửa pipeline Python (sprite-lab, gamekit pipeline, dashboard) | `tools/free-tools/venv/bin/ruff check <path> --select F401,F841,F821,F541` (bắt bug nhẹ); toàn bộ linter ở `tools/free-tools/README.md` |
| Kiểm GDScript khác ngoài gamekit test | `tools/free-tools/venv/bin/gdlint src/` trong game (chỉ đọc; không `--fix` hàng loạt) |
| Tạo art bằng AI / ComfyUI / diffusion | `tools/gpuhost/gpuhost` (GPU `desktop-kndgm60`, SSH tunnel, không chạy local). Cài/chạy: `gpuhost init` → `gpuhost start comfyui` → dùng API `127.0.0.1:8190`; xong `gpuhost release comfyui`. Model/output ở `~/gameart-gpu` trên máy GPU, không tải model nặng về laptop, không đụng `~/imagegen-gpu` |
| Thử cảm giác một cơ chế mới (prototype vứt đi, không vào repo game) | `tools/craft-anything/ca rebuild - "<mô tả>" --rounds 1 --unattended --allow-run --backend "Claude Code" --build-with godot` (cài một lần: `tools/craft-anything/install.sh`). Dùng **Claude Code của bạn** nên tốn quota, không tốn tiền mới. Chỉ để thử: **không** copy asset của game khác, **không** copy code sinh ra vào `games/<g>/`, xoá `tools/craft-anything/projects/<slug>/` khi xong. Chi tiết + kết quả đo: `tools/craft-anything/README.md` |
| Thiết kế art trước khi vẽ (tránh thiết kế mò) | skill **`.agents/skills/art-reference/SKILL.md`**: tra `art-refs/palettes/` và LPC `spritesheets/`; **bắt buộc** thêm tra Internet (game cùng thể loại / phong cách pixel gần): xem mẫu chính thống công khai, ghi lại 3 dòng (học gì / tránh gì / quyết định của mình), không có Internet thì nói rõ đã bỏ bước này. Tuân `art-refs/ATTRIBUTIONS.md` |
| "Thêm tính năng" (lớn, nhiều hệ thống) | `/quick-design` (thay đổi nhỏ) hoặc `/design-system` → `/create-stories` → `/dev-story` → `/story-done` |
| "Game khó/dễ quá", "chỉnh tốc độ…" | sửa `assets/data/*.json` (không hardcode trong code) → `/balance-check` → `gamekit test` + `gamekit shot` |
| "Thêm nhân vật", "sprite người/quái dạng người" | `gamekit lpc` (người dùng phối đồ, xuất **ZIP split animations**) → chép vào `games/<g>/assets/source/lpc/<tên>.zip` → `gamekit sprites <g>` → `gamekit preview <g> <tên>` → dùng `LpcCharacter` trong code |
| Sprite / art pixel (nhân vật, quái, icon, hiệu ứng, tile; không phải LPC), thử animation, thử di chuyển | skill **`.agents/skills/pixel-sprite/SKILL.md`**, làm trong **Sprite Lab** (`sprite-lab/`, không bao giờ trong game). Nhân vật có tay chân/vũ khí: ưu tiên nguồn pose rig `gamekit art rig new` → validate/inspect/motion → `gamekit art run` → xem `preview.png` → `gamekit art shot <tên> sheet` + `… move` → `gamekit art test`; art không phù hợp rig: `gamekit art new` → sửa `gen.py` → cùng bước render/review/test; commit repo gốc → khi game cần: `gamekit art promote <tên> <g>`; hướng nghệ thuật bằng `/art-bible`, `/asset-spec` |
| Menu, HUD, giao diện | **tham khảo trước**: tìm cách ≥ 2 game cùng thể loại làm màn đó (wiki, ảnh chụp, bài phân tích), ghi nguồn + điều lấy vào `design/ux/<màn>.md` mục "## Tham khảo" (test `ux_spec_test.gd` của game chặn màn menu thiếu spec) → dựng bản thử trên web ở `design-web/` (`design-web/serve.sh`, mỗi màn 1280×720, bàn phím là input chính, **không** làm như trang web) → chốt bằng ảnh 1280×720 → `/ux-design` → `/team-ui`; bắt buộc chụp lại bằng `gamekit ui-shots <g>` và soi từng vùng ×2 |
| Âm thanh (tiếng hiệu ứng, nhạc nền) | `gamekit audio <g>`: tham số trong `games/<g>/assets/source/audio/sfx.json` (kiểu sfxr) + `music.json` (tracker) → `assets/audio/**.wav`; **xem** `production/audio/review.png`, người dùng nghe bằng `--play <id>`; sự kiện → tiếng ở `assets/data/audio.json` của game; `gamekit audio test`. Thiết kế lớn hơn: `/team-audio` |
| "Game bị lỗi…" | `/bug-report` → viết test hồi quy, **chạy cho thấy test fail trước** → sửa → `gamekit test` |
| "Review code" | `/code-review` của game (bản scoped `games/<g>`), không dùng bản chung |
| "Chơi thử / chạy xem" | `gamekit run <g>` (người chơi), `gamekit shot <g> [scene] [frames] [-- args]` (agent tự nhìn; nhiều thời điểm thì một lần chạy `frames=300,600,900`, tua nhanh bằng cờ của game như `--sim-steps`) |
| "Giờ làm gì tiếp?", "dự án tới đâu rồi?" | `/next-step`, `/project-stage-detect` |
| "Xuất game", "build", "phát hành" | tăng `config/version` trong `project.godot` → `gamekit export <g>` → `gamekit smoke-web <g>` → `/release-checklist`, `/patch-notes` |
| "Cập nhật framework" | `gamekit update-template`; với từng game, làm theo `UPGRADING.md` của template, rồi `gamekit tidy <g>` (bỏ lại agent của engine khác) |
| Thư mục game lẫn file của framework (README/CHANGELOG/.github của tool) | `gamekit tidy <g>` (gamekit new đã tự chạy) |
| "Thêm/sửa skill hoặc cấu hình agent" | sửa `.agents/skills/` hoặc `AGENTS.md` → `gamekit agents-link` → `gamekit doctor` |
| "Sửa/mở rộng bộ công cụ" | sửa `tools/gamekit` → tăng `tools/gamekit/VERSION` → `gamekit install <g>` cho mỗi game → `gamekit test <g>` |
| Bắt đầu ngày làm việc | `gamekit update-tools` (pull template + LPC generator, báo phiên bản công cụ); `gamekit doctor` và `gamekit test` nhắc khi hôm nay chưa chạy |
| Máy mới, lệnh lỗi, thiếu phần mềm | `gamekit doctor` |

## Quy tắc chung

- **Nhìn tận mắt rồi mới báo xong.** Thay đổi nào người chơi thấy được thì phải chạy game và xem ảnh
  (`gamekit shot`); ảnh dùng làm bằng chứng lưu ở `games/<g>/production/qa/evidence/`. Parse được code
  chưa có nghĩa là game chạy được.
- **Soát giao diện ở độ phân giải thật, phóng to từng vùng** (×2): xem ảnh cả màn chỉ để thấy bố cục; sau đó cắt
  từng khối (thanh HUD, từng thẻ, từng khung) và kiểm: icon và chữ cùng một đường tâm, chữ nằm giữa thanh/nút theo
  chiều dọc, nội dung thẻ/khung căn từ trên xuống (không căn giữa dọc: người dùng thấy xấu, 2026-11-17) và các
  thẻ cùng hàng cao bằng nhau theo nội dung dài nhất, khoảng cách đều, không gì bị cắt hay tràn khung, chữ đọc
  được trên nền. Vị trí
  chữ tính theo cỡ font (không gõ baseline tay). Ghi các lỗi tìm được rồi mới sửa (bài học 2026-11-17).
- **Nhân vật/sprite mới: đưa 2–3 thiết kế khác nhau để chọn** (người dùng 2026-11-21): khác silhouette, tỉ lệ,
  cách cầm vũ khí, dáng và nhịp animation, không chỉ đổi màu. Model AI (`gamekit art concept`) chỉ để lấy ý tưởng
  ban đầu, không tham gia thiết kế. Chi tiết: skill `pixel-sprite` bước 0.
- **Chỉ sửa đúng cái người dùng chỉ ra** (người dùng 2026-11-22): một nhận xét chung đi kèm yêu cầu cụ thể (ví dụ "game 2D nên thiết kế kiểu 2D") chỉ áp cho những thứ được chỉ; thứ khác có thể liên quan thì liệt kê và hỏi trước, không tự sửa (đã lỡ vẽ lại ấn Cột thánh quang, phải hoàn tác).
- **Việc "tạm dừng" / "tuỳ chọn" trong tài liệu không phải việc còn dở** (người dùng 2026-11-23): không đưa vào danh sách việc cần làm và không làm tiếp khi chưa hỏi; khi báo việc còn lại, ghi rõ "tuỳ chọn, chỉ làm khi bạn muốn" (đã lỡ vẽ lại Chém kiếm, vốn chỉ là nhầm tên với Sóng kiếm).
- **Cỡ nhân vật chốt: nhỏ, minifig 48×48 (thân ~26 px)** (người dùng 2026-11-22, sau khi thử bản ~40 px trong
  64×64): nhân vật mới và nhân vật hiện có giữ cỡ này. `sprite-lab/lib/hdfig.py` và các sprite `*-hd` chỉ là
  thử nghiệm, không dùng cho game. Thay đổi duy nhất được giữ là bước đầu: dùng model AI (`gamekit art concept`)
  để lấy ý tưởng ngoại hình, rồi thiết kế/vẽ như cũ.
- **Không đoán mò khi thiết kế** (người dùng 2026-11-17): màn hình, luồng menu, tính năng mới đều bắt đầu từ cách
  các game cùng thể loại đã làm (tìm trên mạng), ghi nguồn vào tài liệu thiết kế rồi mới code. Thiếu thông tin
  mà tham khảo không trả lời được thì hỏi người dùng. Từ ngữ của người dùng ứng với hơn một hệ thống của game
  (ví dụ "mốc 10/20/30": ải hay cấp trong trận?) cũng là thiếu thông tin: hỏi lại trước khi làm.
- **Đánh giá tool/dependency mới: đọc `--help`, chạy một thử nghiệm nhỏ rồi mới kết luận** (2026-11-23):
  kết luận "vô dụng" chỉ từ README đã suýt loại `craft-anything`, trong khi nó có nhánh dựng-từ-mô-tả.
  Một thử nghiệm 12 phút rẻ hơn một quyết định sai.
- **Prototype bằng `tools/craft-anything` là để thử, không để ship** (người dùng 2026-11-23): nó dựng một
  project mới từ mô tả (không addon gamekit, art placeholder, chỉ self-test của nó) trong
  `tools/craft-anything/projects/` (gitignored). Thử cảm giác xong thì xoá; tính năng thật làm trong
  `games/<g>` theo pipeline thường. Không copy asset của game khác, không dùng Deep mode trên game mình
  không sở hữu. Chi tiết: `tools/craft-anything/README.md`.
- **Giao diện hiện tại** của game là `production/ui/` (danh sách màn hình trong `production/ui/screens.json`):
  đổi thứ người chơi thấy thì chạy `gamekit ui-shots <g>`, xem ảnh, commit `production/ui`. Dashboard (`games.html`)
  chỉ hiện bộ này và báo khi nó cũ hơn code; ảnh trong `production/qa/evidence/` là bằng chứng lịch sử, không phải
  giao diện hiện tại.
- **Thiết kế màn hình trên web trước khi vào Godot** (người dùng 2026-11-22): dựng ở `design-web/` — mỗi màn một
  file `screen-<tên>.html` cố định **1280×720**, font pixel, bàn phím/focus là chính; không cuộn, không thanh
  điều hướng, không card bo tròn kiểu web. Chốt bằng ảnh 1280×720 trong `design-web/shots/` và đặc tả
  `design-web/screens/<tên>.md` (có mục "## Tham khảo"), rồi mới port sang `games/<g>/src/...` và chạy
  `gamekit ui-shots`. Tool/asset tham khảo miễn phí tải bằng `design-web/setup.sh`.
- **Tiết kiệm RAM/thời gian** (người dùng 2026-11-21: làm lâu, ngốn RAM): `gamekit ui-shots <g> <tên màn…>` chỉ chụp lại các màn vừa đổi (mỗi màn là một Godot render bằng CPU trên Xvfb); chụp cả bộ chỉ trước khi xuất bản web. Tra code bằng `tools/gdgraph` / graphify thay vì đọc cả file lớn (`run.gd` > 3000 dòng).
- **Chụp nhanh:** cần nhiều ảnh thì **một** lệnh `gamekit shot <g> "" 300,320,340 -- …`, không gọi `shot` lặp lại
  trong vòng lặp (mỗi lần là một lần mở Godot và chạy lại từ đầu). Cảnh muộn trong game thì tua bằng cờ của game
  (ví dụ `--sim-steps=4`), không chụp ở frame 1500.
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
- **Lọc output không được che lỗi:** lệnh `gamekit … | tail` (hoặc `| grep`) nối `&& git commit` thì phải `setopt pipefail` trước (zsh), nếu không exit của gamekit bị mất và commit vẫn chạy (bài học 2026-11-21).
- **Shell là zsh.** Không dựa vào word splitting (`set -- $s`, `for x in $list` với chuỗi có dấu cách): gọi
  từng lệnh riêng hoặc dùng mảng. **Không gom nhiều đường dẫn vào một biến** (`L="a b"; git add $L` hỏng):
  viết thẳng các đường dẫn vào lệnh. Script trong `tools/gamekit` viết bằng bash (`#!/usr/bin/env bash`).
- **Mỗi ngày làm việc pull bản mới nhất của công cụ đang dùng** (người dùng 2026-11-17): chạy
  `gamekit update-tools` trước việc đầu tiên trong ngày. Pull lỗi (có thay đổi cục bộ, lệch nhánh) thì dừng và
  báo, không ép. Template mới không tự đổi game: nâng game theo `UPGRADING.md` của template.
- **Tên trong game bằng tiếng Việt** (người dùng 2026-11-17): tên chiêu, thẻ, quái, vật phẩm, buff mà người
  chơi thấy đều là tiếng Việt; id, tên file, tên sprite giữ tiếng Anh. Test
  `tests/integration/data/vietnamese_names_test.gd` của game chặn tên không dấu (trừ danh sách cho phép).
- **Sprite đặt theo điểm neo, không theo tâm canvas.** Sprite nào cũng có `<tên>.json` (do `gen.py` gọi
  `write_meta`) và game vẽ qua `SpriteAnchor`. Chi tiết trong skill `pixel-sprite`.

## Điều tra code (graphify)

- **Tối ưu đọc/điều hướng code trước** (ổn định, local, miễn phí): dùng `graphify` (CLI/skill) cho câu hỏi "ở đâu / gọi cái gì / liên kết thế nào", sau đó **chỉ đọc đúng file/line** được chỉ và xác minh trong source trước khi sửa.
- **Duy trì index AST cục bộ** (không cần LLM, chạy qua `limited`): đầu mỗi ngày làm việc hoặc khi code vừa thay đổi nhiều, chạy `limited graphify update tools/gamekit` và `limited graphify update sprite-lab` (~10 s mỗi cái, giữ index mới thì `explain` mới đúng).
- **Python/tool**: chỉ hai khu vực trên. `graphify` 0.9.104 **không đọc GDScript** (kiểm 2026-11-21: index `games/bach-ai` ra **0** node `.gd`, chỉ nhặt 4.892 file `.md` trong `.claude/`) — đừng chạy `graphify update` trên `games/`, `templates/`, `tools/lpc-generator/`. Index cũ mà vẫn trả lời thì câu trả lời sai theo code cũ: `explain` báo "No node matching" nghĩa là index chưa phủ symbol/ngôn ngữ đó, chạy lại `update` rồi mới kết luận.
- **GDScript**: dùng `limited tools/gdgraph/gdgraph games/<g>` (~0,5 s) rồi truy vấn cùng lệnh `graphify explain/path/query --graph games/<g>/graphify-out/graph.json`; cài đặt và giới hạn ở `tools/gdgraph/README.md`. `explain "<tên>"` (không có `()`), tên trùng nhiều file thì dùng `"<file>.gd::<tên>"`; test `tools/gdgraph/.venv/bin/python -m unittest discover -s tools/gdgraph -p 'test_gdgraph.py'`.
- **Truy vấn**: `graphify explain "<symbol>" --graph <khu-vực>/graphify-out/graph.json`, `graphify path "A" "B" --graph <khu-vực>/graphify-out/graph.json` (hoặc dùng đường dẫn mặc định nếu đang ở đúng khu vực). Ví dụ tiết kiệm thật: `explain "earth_burst"` trả 900 byte kèm số dòng cho 11 chỗ gọi, thay vì đọc cả `burstfx.py` (441 dòng, 21 KB); `explain "_step_meteors"` trả 793 byte thay vì `run.gd` (3.269 dòng, 139 KB).
- **Quy ước**: `graphify-out/` là artifact sinh ra, **không commit**. Thay đổi rộng hoặc codebase lạ: cập nhật/đọc graph trước rồi mới sửa.

## Âm thanh báo (người dùng 2026-11-18)
- Chạy `gamekit notify` sau khi một task đã kiểm chứng xong (và ngay trước khi hỏi người dùng để xin chấp thuận/ý kiến).
- File là `tools/gamekit/assets/notify.wav` — chuông hai nốt, tự sinh bằng code, ~0,58 s. `gamekit notify` thử `paplay` → `aplay` → `canberra-gtk-play`; không có player thì chỉ in cảnh báo, không dừng việc.
- Mỗi lượt làm việc báo một lần, sau khi commit. Không dùng cho từng bước nhỏ.

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
  **Ngoại lệ:** commit kèm đường dẫn lấy nội dung **trên đĩa**, nên không ghi được việc "thôi theo dõi"
  (`git rm --cached` mà file vẫn còn): file sẽ bị commit lại. Trường hợp đó, xem stage chỉ còn đúng thay đổi
  ấy rồi commit **không** kèm đường dẫn.
- **Xem stage ở một lệnh riêng**, đọc xong mới commit: `git diff --cached --stat -M` không được nối `&&`
  với `git commit` (nối thì không kịp đọc). Một lệnh commit lỗi thì dừng, kiểm tra index rồi mới làm tiếp.
- Sửa `.gitignore`: pattern chỉ dành cho thư mục gốc phải có `/` đầu (`/templates/`), rồi chạy `git status`
  xem có file nào vừa biến mất khỏi danh sách.
- Commit kèm file `.uid` mà Godot sinh ra cạnh script/shader (quy tắc của framework); **không** commit `.godot/`,
  `builds/`, file tạm, log, `*.import` của file bị xóa, hay credential/khóa ký.
- **Có** commit: `export_presets.cfg`, `assets/source/lpc/*.zip`, `sprite-lab/sprites/<tên>/` (gen.py, strip, json, hitmask; **không** GIF và `preview.png`: sinh lại bằng `gamekit art run`, đã ở `.gitignore` từ 2026-11-21),
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

- **`git show --stat HEAD`** và so với danh sách file định commit: commit thiếu file (ví dụ một agent khác vừa
  khôi phục thư mục đó) thì dừng, tìm lại thay đổi (`git fsck --unreachable` giữ các blob đã `git add`), rồi mới
  báo. Chỉ báo "đã commit" khi danh sách khớp.
- Có agent khác đang chạy cùng workspace (`pgrep -af "claude|opencode|codex"`): commit **ngay** khi một phần
  việc đã kiểm tra xong, không để việc đã xong nằm chưa commit sang lượt sau.
- Báo cho người dùng **hash và subject** của từng commit (ghi rõ repo nào).
- **Không push** trừ khi người dùng yêu cầu. Không `--amend` commit đã push, không `--force`, không `--no-verify`
  (hook của framework là lớp bảo vệ, không được lách).
- Hook commit của game chỉ chạy với Claude Code mở trong `games/<g>/`. Agent khác, hoặc commit từ repo gốc,
  vẫn phải tự tuân thủ các mục kiểm tra ở trên.
