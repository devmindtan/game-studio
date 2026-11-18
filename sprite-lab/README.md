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
├── tests/                    unit (SpriteSheet, SpriteAnchor, SpriteHitbox) + integration (mọi sprite hợp lệ)
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
Hiệu ứng gây sát thương khai báo `"hitbox"` cho animation (xem skill `pixel-sprite`): `art run` đo và kiểm tra nó
từ pixel, ảnh `art shot <tên> sheet` vẽ hitbox (đỏ = frame gây sát thương).
Nhân vật mặc được đồ vẽ theo ô trang bị (`minifig.draw_layers` + `sheet.export_layered`): thân, giáp đầu, giáp
ngực, giáp tay, giáp chân, vũ khí (`minifig.SLOTS`); xem `layers.png`, các lớp nằm trong `layers/`; `art run` kiểm
tra ghép lớp trùng từng pixel với strip.

## Xem trên web (`./serve-viewer.sh`)

`./serve-viewer.sh` (trong `sprite-lab/`) chạy server ở gốc workspace (chỉ `127.0.0.1`) và mở
http://localhost:8765/sprite-lab/viewer.html. `NO_OPEN=1 ./serve-viewer.sh` thì không mở trình duyệt (agent, test).

### Sprite Lab (`viewer.html`)

Danh sách mọi sprite theo nhóm, khung xem lớn (tỉ lệ "Vừa khung", nền caro/tối/sáng/cỏ, đường đất + điểm neo),
dải frame có thời lượng từng frame (bấm để nhảy tới), GIF và preview sheet. Phát đúng `durations_ms`.

- **Tự cập nhật**: mỗi 2 giây viewer đọc lại manifest; `gamekit art run <tên>` tạo lại manifest, nên sprite vừa
  vẽ hiện ngay, không cần F5. URL ảnh mang `?v=<mtime>` nên trình duyệt không dùng ảnh cũ.
- **Đường dẫn nhớ vị trí**: `viewer.html#mage/attack`.
- **Phím**: Space phát/dừng · ←/→ frame · ↑/↓ animation · 1–9 chọn animation · `[` `]` sprite trước/sau ·
  `+`/`-` tỉ lệ · B nền · V chế độ màu · R từ đầu · `/` tìm.

### Game dashboard (`games.html`)

Toàn bộ những gì một game đang có, đọc thẳng từ repo game (`build_games_manifest.py`, server dựng lại mỗi lần
trang tải), để xem và quyết định có áp dụng vào game không:

| Mục | Nội dung |
|---|---|
| Tổng quan | pitch, thể loại, câu hỏi thiết kế, bảng "Đã quyết" của roadmap, ảnh mới nhất |
| Luật gameplay | luật trong `games/<g>/assets/data/gameplay_rules.json` + bảng chấm mọi kỹ năng của game |
| Giao diện | bộ màn hình hiện tại `production/ui/` (chụp bằng `gamekit ui-shots <g>`), báo khi ảnh cũ hơn code |
| Bản đồ & ải | bãi đấu vẽ đúng nền cỏ của game, vòng spawn, khung màn hình; biểu đồ đợt quái theo thời gian |
| Nhân vật | animation, 5 ô trang bị bật/tắt được (giáp đầu, ngực, tay, chân, vũ khí), chỉ số kèm icon |
| Quái vật | animation cùng tỉ lệ game, thân đo từ pixel, chỉ số, xuất hiện ở ải nào |
| Kỹ năng | demo như trong game (nền bản đồ thật, slime làm hình nhân, chớp đỏ + số sát thương + thanh máu), nút "Khoảnh khắc trúng", bảng giá trị từng cấp, nâng cấp chỉ số; đường dẫn `games.html#<g>/skills/<kỹ năng>/hit/<cấp>` mở thẳng lúc trúng |
| Vật phẩm | mọi vật phẩm trong `assets/data/items.json`: đồ nhặt trong ải (kèm số liệu) và trang bị |
| Hiệu ứng | hiệu ứng trạng thái vẽ lên người (buff/debuff: chảy máu, bỏng, độc…, cho mọi nhân vật); trống khi game chưa có |

**Rule góc nhìn skill demo** (người dùng 2026-11-18): mọi chiêu dùng một góc nhìn cố định (`BASE_Z` trong
`games.html`), không tự phóng to theo kích thước sprite — chiêu nhỏ đừng phóng to, chiêu lớn vẫn thấy toàn bộ
vùng. Chỉ nút `−` / `+` mới đổi tầm nhìn. Khi thêm hoặc sửa demo chiêu, giữ nguyên rule này.

**Rule khung quái vật** (người dùng 2026-11-18): quái trong tab Quái vật luôn nằm gọn toàn bộ trong card.
Giữ tỉ lệ game khi vừa, tự co lại theo kích thước frame khi là boss to; tuyệt đối không cụt đầu/cụt chân.
Đồng thời header dashboard hiện mốc `Dữ liệu web` (thời điểm rebuild manifest) để biết trang đang tải dữ liệu mới.

**Rule hiệu ứng từ tâm** (người dùng 2026-11-19): chiêu triển khai ngay tại tâm nhân vật (`under_hero` trong
`upgrades_*.json`, ví dụ Đậm đất / Lốc xoáy) phải vẽ hiệu ứng **trước** nhân vật để nhân vật không bị đè.
Ngược lại, hiệu ứng nào to hơn khung demo thì tự co lại (`fitView`) cho thấy toàn bộ; chiêu nhỏ vẫn giữ một
góc nhìn cố định, không tự phóng to.

Trang chỉ để xem; đánh giá và quyết định trao đổi trực tiếp với agent. Script dựng manifest và server **chỉ đọc**
repo game.

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
