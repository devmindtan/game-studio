# Craft Anything (tùy chọn) — lò prototype vứt đi

[storytold/craft-anything](https://github.com/storytold/craft-anything) dựng **một project mới** từ mô tả
của bạn, tự build, tự chạy self-test, tự chụp ảnh, rồi tự tinh chỉnh vài vòng. Nó không có model riêng:
phần "AI viết code" là **agent của bạn** (ở đây: Claude Code đã đăng nhập sẵn).

Dùng để trả lời nhanh câu hỏi kiểu *"sóng quái dày thế này có vui không?"* trước khi viết vào game thật.
**Không** dùng để làm tính năng thật: code sinh ra là một project riêng, không có addon `gamekit`,
không có sprite pipeline, không có test của game.

## Cài

```sh
tools/craft-anything/install.sh
```

Tải `.deb` bản ghim (`0.6.1`, ~68 MB) từ GitHub rồi **giải nén vào `tools/craft-anything/app/`** —
không `sudo`, không cài gì vào hệ thống. Script đăng ký backend Claude Code một lần, rồi chạy `doctor`.

Bản giải nén (134 MB), cấu hình và project đều nằm trong thư mục này và **không commit**:

| Đường dẫn | Nội dung |
|---|---|
| `app/` | bản giải nén từ `.deb` (xoá được, cài lại bằng `install.sh`) |
| `state/` | `XDG_CONFIG/DATA/CACHE_HOME` riêng, không đụng `$HOME` |
| `projects/` | project prototype sinh ra |

## Dùng

```sh
# prototype mới, 1 vòng tinh chỉnh, không hỏi gì
tools/craft-anything/ca rebuild - "Một màn survivor 2D bằng Godot 4: nhân vật 48x48 đi WASD,
quái theo sóng từ 4 phía, tự bắn quái gần nhất, ngọc XP, 3 thẻ nâng cấp chọn bằng 1/2/3,
sống 90 giây, HUD tiếng Việt. Có --self-test chạy headless in số quái giết và cấp đạt được." \
  --rounds 1 --unattended --allow-run --backend "Claude Code" --build-with godot
```

- `-` ở vị trí `<TARGET>` = **không có bản gốc**, chỉ dựng từ mô tả (đây là cách dùng chính ở đây).
- `--build-with`: `godot`, `unity`, `unreal`, `rust`. Mặc định game là Unity, nên ghi rõ Godot.
- `--rounds 1`: một vòng tinh chỉnh là đủ cho prototype; nhiều vòng ăn quota Claude.
- `--unattended --allow-run`: không hỏi giữa chừng (bắt buộc khi agent chạy nền).
- Project ra ở `projects/<slug>/app/`; chạy thử: `godot --path projects/<slug>/app`.

Wrapper tự thêm `--projects-dir`, tự bọc `limited` để giữ tài nguyên máy, và tự đặt XDG vào `state/`.

## Kết quả đo được (2026-11-23)

Prototype "màn survivor 90 giây, HUD tiếng Việt" — **12 phút**, 1 vòng, backend Claude Code:

- `Ready: 3/4 check đạt, 8/8 claim đúng`; check thứ 4 ("so mechanics với bản gốc") bỏ trống vì không có bản gốc.
- Self-test tự chạy lại: 25 quái hạ, cấp 4, đủ 8 mục `move/act/hud/waves/xp/level_up/survive/win_at_90s` đạt.
- Ảnh tự chụp: HUD tiếng Việt có dấu đúng, màn lên cấp 3 thẻ chọn bằng 1/2/3.
- Nó tự cân bằng: tăng máu quái → bot gục giây 26; giảm → thắng trọn; chốt mức giữa.
- Chất lượng code: **834 dòng trong một `game.gd`**, không asset, `MECHANICS.md` 58 thông số (46 tự đặt).

Kết luận: đủ tốt để **thử cảm giác**, chưa đủ để đưa vào game.

## Rule khi dùng trong workspace này

- **Chỉ prototype, vứt đi.** Không `gamekit art promote`, không copy sang `games/<g>/src`. Cần tính năng thật
  thì làm trong game theo pipeline thường (`gamekit new`, test, `gamekit shot`).
- **Không copy asset của game khác.** Clean room (mặc định) không đọc file bản gốc. Deep mode chỉ dùng trên
  phần mềm **bạn sở hữu hoặc được phép xem**; dùng Deep mode thì phải có `CREDITS.md` như tool yêu cầu.
- **Không commit project prototype.** Nằm trong `projects/` (đã gitignore); xong việc thì xoá.
- **Art** là hình khối placeholder. Ảnh/model sinh bằng AI phải bật `--generate-assets` và có key fal.ai
  **trả phí** — workspace này không dùng; art thật làm ở `sprite-lab/`.
- **Chi phí** là quota Claude của bạn, không phải tiền mua thêm. Một vòng có thể chạy lâu; giữ `--rounds 1`.
- **Máy**: wrapper đã bọc `limited`; đừng chạy song song với `gamekit shot`/export.

## Giấy phép

Craft Anything: MIT hoặc Apache-2.0 (chọn một). Bản `.deb` tải từ GitHub Releases chính thức.
Đây là **alpha** (0.6.1): hành vi có thể đổi giữa các bản; nâng bản bằng
`CRAFT_ANYTHING_VERSION=<x.y.z> tools/craft-anything/install.sh`.
