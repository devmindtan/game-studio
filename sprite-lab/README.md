# Sprite Lab

Nơi **duy nhất** để làm và thử sprite pixel art của workspace. Sprite làm xong và đạt mới được chép
sang game cần dùng. Lab là một project Godot riêng: không phải game, không bao giờ được export.

```text
sprite-lab/
├── sprites/<tên>/            mỗi sprite một thư mục (nguồn duy nhất)
│   ├── gen.py                code vẽ: palette, ASCII map, các animation, điểm neo
│   ├── <tên>_strip.png       mọi frame, trái sang phải, animation nối tiếp nhau
│   ├── <tên>.json            frame_size, điểm neo, animation {name, start, frames, fps, loop}
│   ├── <tên>.png             frame đầu (icon)
│   ├── preview.png           mỗi animation một hàng, phóng to có lưới (agent đọc)
│   └── <animation>.gif       chuyển động (người xem)
├── lab/sprite_lab.tscn       trình thử: chế độ sheet và move
├── tests/                    unit (SpriteSheet, SpriteAnchor) + integration (mọi sprite hợp lệ)
└── addons/gamekit/           bản sao addon (gamekit tự cài, git bỏ qua)
```

## Quy trình

| Bước | Lệnh | Đạt khi |
|---|---|---|
| 1. Tạo | `gamekit art new <tên> [--size N]` | có `sprites/<tên>/gen.py` |
| 2. Vẽ | sửa `gen.py`: chốt kích thước, palette, **điểm neo**, danh sách animation | |
| 3. Render + kiểm tra | `gamekit art run <tên>` | in ra metadata, không báo lỗi |
| 4. Xem tĩnh | mở `sprites/<tên>/preview.png` | silhouette đọc được ở 1x, frame đổi 1–2 px |
| 5. Thử sheet | `gamekit art shot <tên> sheet` (hoặc `gamekit art lab <tên>`) | mọi animation chạy, chân/neo nằm trên đường đất, không giật |
| 6. Thử di chuyển | `gamekit art shot <tên> move` | ảnh lưới 8 khoảnh khắc: đi phải, đánh, đứng, chạy trái (lật), nhảy, đi trái, phép, trúng đòn; lật hướng không xê dịch neo |
| 7. Test | `gamekit art test` | mọi test qua |
| 8. Commit | repo gốc (lab nằm trong repo gốc) | |
| 9. Đưa vào game | `gamekit art promote <tên> <game>` → dùng trong code → `gamekit test`, `gamekit shot` → commit repo game | |

Bước 9 chỉ làm khi game thật sự cần sprite đó. Thử nghiệm không bao giờ diễn ra trong game.

### Nhân vật có tay chân và vũ khí: Pixelbolt pose rig

Gamekit tích hợp Pixelbolt 0.17.0 cho nguồn nhân vật có khớp tương đối và attachment. Bản nguồn là
`sprites/<tên>/<tên>.poses.json`; build compile bằng Pixelbolt rồi chuyển atlas sang định dạng strip của
Sprite Lab. Timing frame không đều được giữ trong `durations_ms` và phát đúng trong `SpriteSheet`.

```sh
npm ci --prefix tools/gamekit                   # chỉ lần đầu, Node.js 20+
gamekit art rig new swordsman hero-sword
gamekit art rig validate swordsman
gamekit art rig inspect swordsman attack
gamekit art rig motion swordsman walk 24
gamekit art run swordsman
gamekit art shot swordsman sheet
gamekit art shot swordsman move
gamekit art test
```

Pixelbolt cung cấp cấu trúc và diagnostics; người thiết kế vẫn phải xem silhouette ở kích thước gốc, các pose
chính, vũ khí qua các frame và playback thực tế. Hãy truyền tốc độ gameplay thật vào `motion`; mặc định 24
px/s chỉ là tốc độ kiểm tra khởi đầu. Sprite dùng `gen.py` vẫn hỗ trợ đầy đủ như trước.

### Nhân vật nhỏ gọn: `lib/minifig.py`

Bộ dựng nhân vật nhìn ngang, tối giản (khung 48×48, cao ~26–30 px, neo (24, 44) trên đất): mỗi frame là
một tư thế bằng số (`bob`, `lean`, `feet`, `hands`, `weapon`, `eyes`, `lie`, `flash`, `fx`…), nên tỉ lệ cơ thể
không đổi giữa các animation. Có sẵn thân `tunic` (áo + quần) và `robe` (áo choàng), chu kỳ chạy 8 frame,
nháy trắng khi trúng đòn (giữ viền), ngã xoay về đất, và `keep_above_floor` để vũ khí không xuyên đất.
Nhân vật dùng `write_anim_meta(..., ground=True)`: `art run` kiểm tra mọi frame chạm đất.

## Trình thử (`gamekit art lab [<tên>] [sheet|move]`)

- **sheet**: mọi animation cạnh nhau, mỗi cái lặp lại (animation một lần thì nghỉ 0,6 giây rồi chạy lại),
  có đường đất ở độ cao điểm neo, chấm neo hồng và khung frame.
- **move**: sân thử. Sprite có animation `jump` là nhân vật đi trên mặt đất (←/→ đi, Shift chạy, Space nhảy);
  sprite không có `jump` thì bay hoặc nhìn từ trên (←↑↓→). J đánh, K phép, H trúng đòn, X chết, R đặt lại.
  Animation được chọn theo tên: `idle`, `walk`/`run`/`fly`/`move`, `jump`, `attack`, `spell`, `hurt`, `death`.
- Tab đổi sprite, M đổi chế độ, B đổi nền (tối/sáng/caro), +/- tỉ lệ, A bật tắt neo và khung.
- `--demo` chạy kịch bản 9 giây; `--contact=<png>` chụp 8 khoảnh khắc thành một ảnh rồi thoát
  (đó là cách `gamekit art shot … move` hoạt động).

## Trong game

`gamekit art promote` chép `<tên>_strip.png`, `<tên>.png`, `<tên>.json` vào
`games/<g>/assets/sprites/custom/<tên>/`, kèm `"source": "sprite-lab/sprites/<tên>"` trong json. Game vẽ bằng
`SpriteSheet` / `SpriteAnchor` trong `addons/gamekit/sprites/`. Muốn sửa sprite: sửa trong lab, chạy lại
`art run`, thử, rồi `promote` lần nữa.
