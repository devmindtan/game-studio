# Bài học (lỗi đã gặp → chỗ đã chặn)

Mỗi lỗi do agent gây ra (hoặc người dùng phát hiện) được ghi **một dòng** ở đây, kèm chỗ đã sửa để nó không
lặp lại. Quy trình ở mục "Sai một lần → sửa rule" trong `AGENTS.md`. Đọc file này trước khi làm việc cùng loại.

Cột "Chặn bằng" ưu tiên theo thứ tự: **công cụ / test tự kiểm tra** > rule trong skill hoặc `AGENTS.md` > ghi chú.

| Ngày | Lỗi (triệu chứng → nguyên nhân gốc) | Chặn bằng |
|---|---|---|
| 2026-11-16 | Sprite lệch tâm, đom đóm giật 3px khi quay đầu → code căn theo **tâm canvas** trong khi hình không nằm giữa canvas; số frame/anchor khai báo tay trong config | `spritekit.write_meta` ghi `<tên>.json` (frames, fps, **anchor**); `gamekit art run` báo lỗi nếu thiếu hoặc sai; game đặt sprite bằng `SpriteAnchor` (có unit test lật hướng); integration test so `.json` với strip; skill `pixel-sprite` bước 1 bắt buộc chốt anchor |
| 2026-11-16 | Sprite lật hướng bị vẽ lệch một chiều rộng sprite → tự tính lại gốc rect khi dùng chiều rộng âm (Godot giữ nguyên vùng vẽ) | `SpriteAnchor.dest_rect` + unit test; skill: không tự tính rect, dùng helper |
| 2026-11-16 | Pixel art nhòe khi phóng to → project dùng bộ lọc tuyến tính mặc định | template `project.godot` có `default_texture_filter=0`; skill ghi rõ |
| 2026-11-16 | Đốm sáng/sprite quá mờ, quầng lệch → chỉ xem preview, chưa xem trong game | `AGENTS.md`: thay đổi nhìn thấy được phải `gamekit shot` và **xem ảnh**; `--debug-anchors` để kiểm vị trí |
| 2026-11-16 | Bộ chạy test bỏ qua file test lỗi cú pháp mà vẫn báo qua | `run_tests.gd` tính file không load được là FAIL (đã thử bằng file test hỏng) |
| 2026-11-16 | Lỗi trong `main.gd` chỉ lộ ra khi chạy game → test không nạp script chính | integration test sprite `preload` `main.gd`; vẫn bắt buộc `gamekit shot` |
| 2026-11-16 | Godot import `credits.csv` thành file dịch `.translation` | `lpc_ingest.py` ghi `.import` với `importer="keep"` cho mọi CSV credit |
| 2026-11-16 | Credit LPC tra sai tên (`combat_idle` vs `combat`) → thiếu ghi công 18 file | `lpc_sample_compose.py` tra theo tên export trước, thiếu credit thì exit 1; `lpc_ingest.py` từ chối nhân vật không có credit |
| 2026-11-16 | `.gitignore` gốc ghi `templates/` làm mất luôn `tools/gamekit/templates/` | rule commit: pattern chỉ cho thư mục gốc phải có `/` đầu; sau khi sửa `.gitignore` chạy `git status` xem có file nào biến mất |
| 2026-11-16 | Template framework ignore `export_presets.cfg` và `*.zip` → preset và nguồn art không vào git | `gamekit install` thêm `!export_presets.cfg`, `!assets/source/lpc/*.zip` |
| 2026-11-16 | `gamekit install` tạo lại `studio-tests/` vừa bị `tidy` xóa | install chỉ thêm `.gdignore` vào thư mục đã tồn tại |
| 2026-11-16 | Self-check `spritekit` để rác `/tmp/spritekit-*` | dùng `TemporaryDirectory` |
| 2026-11-16 | `P=$(gamekit shot …)` lấy lẫn log của game → `cp` hỏng | `gamekit shot`: stdout chỉ có đường dẫn, log ra stderr |
| 2026-11-16 | Vòng `for s in "a 16" …; set -- $s` truyền cả chuỗi làm tên sprite → shell là **zsh**, không tự tách từ | `AGENTS.md` mục shell: không dựa vào word splitting; gọi lệnh riêng từng dòng hoặc dùng mảng |
| 2026-11-16 | Commit đầu bị lỗi pathspec, commit kế tiếp nuốt luôn thay đổi đã stage (rename skill vào nhầm commit) | rule commit: trước **mỗi** `git commit` xem `git diff --cached --stat`; một lệnh commit lỗi thì dừng, kiểm tra index rồi mới chạy tiếp |
| 2026-11-16 | Lặp lại lỗi trên ngay sau khi viết rule: file test `git mv` từ trước lọt vào commit "update addon" → `git diff --cached --stat && git commit` nối liền nên không đọc stage | rule: **commit kèm đường dẫn** (`git commit -- <paths>` chỉ lấy đúng các file đó) và xem stage ở một lệnh riêng; đã tách lại 2 commit (chưa push) |
| 2026-11-16 | Cửa sổ game giành focus, phím người dùng gõ chỗ khác làm ván chơi bắt đầu lại | chụp bằng `--demo/--idle` + kiểm tra log; game in `Restart input during demo` khi bị phím ngoài tác động |
| 2026-11-16 | Skill nằm ở `.opencode/skills/` nên Claude Code không thấy | một bản gốc `.agents/skills/`, `gamekit agents-link` tạo link, `doctor` kiểm tra |
