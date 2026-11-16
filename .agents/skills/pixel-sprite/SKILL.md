---
name: pixel-sprite
description: >
  Thiết kế, thử và đưa sprite pixel art vào game trong workspace này: nhân vật, kẻ địch, icon, vật phẩm,
  hiệu ứng, animation, sprite sheet nhiều animation, bản thử di chuyển. Mọi sprite được làm và thử trong
  Sprite Lab (sprite-lab/), không bao giờ làm thẳng trong game. Dùng khi người dùng nhờ vẽ/sửa/thử sprite,
  làm art không phải nhân vật LPC, tạo animation 2D, hoặc làm việc với LibreSprite/.ase.
  English triggers: pixel art, sprite, spritesheet, animation frames, sprite test, movement test,
  LibreSprite, Aseprite, game art, tileset, icon.
---

# Pixel sprite (game-studio)

Agent tự thiết kế bằng code (`gen.py` + `spritekit`) rồi lặp: nhìn ảnh, sửa. Không điều khiển GUI.
**Mọi sprite được làm và thử trong Sprite Lab** (`sprite-lab/`, xem `sprite-lab/README.md`). Chỉ khi một game
thật sự cần thì mới `promote` sang game đó.

> Bài học 2026-11-16 (`LESSONS.md`): một sheet pháp sư không liên quan đã bị tạo thẳng trong game đom đóm, và
> trình xem thử bị nhét vào `main.gd` của game. Giờ `gamekit art new <game> …` bị từ chối.

## Lệnh

```sh
gamekit art new <tên> [--size N]       # sprite-lab/sprites/<tên>/gen.py (mẫu nhiều animation)
gamekit art run <tên>                  # vẽ + kiểm tra metadata (frames, animation, neo)
gamekit art shot <tên> sheet           # ảnh: mọi animation cạnh nhau, đường đất, neo, khung
gamekit art shot <tên> move            # ảnh lưới 8 khoảnh khắc của bản thử di chuyển (demo)
gamekit art lab [<tên>] [sheet|move]   # mở lab để người dùng tự điều khiển
gamekit art test | check | list        # test của lab / kiểm mọi sprite / sprite nào đang ở game nào
gamekit art promote <tên> <game>       # chép strip + json vào games/<g>/assets/sprites/custom/<tên>/
gamekit art ase|open <tên>             # .ase để người chỉnh tay trong LibreSprite
```

### Nhân vật dùng pose rig (Pixelbolt)

Khi thiết kế người/nhân vật có tay chân và cầm vũ khí, ưu tiên nguồn pose có khớp và attachment để giữ tỷ lệ
cơ thể/vũ khí xuyên animation. Pixelbolt được gamekit ghim ở 0.17.0, chạy cục bộ, không cần dịch vụ ảnh:

```sh
gamekit art rig new <tên> [hero|hero-sword|knight]  # tạo <tên>.poses.json trong Sprite Lab
gamekit art rig validate <tên>                       # kiểm tra nguồn pose
gamekit art rig inspect <tên> [animation]            # xem onion-skin và diagnostics
gamekit art rig motion <tên> <walk|run> [px/s]       # kiểm tra tiếp đất/trượt chân/quỹ đạo
gamekit art rig build <tên>                          # render và nhập vào định dạng Sprite Lab
gamekit art shot <tên> sheet && gamekit art shot <tên> move
gamekit art test
```

Chốt brief cạnh nguồn: silhouette và khoảng âm, vai trò từng màu, mặt phẳng sáng, hướng nhìn, điểm neo, điểm
tiếp đất, các pose contact/compression/passing/extension, anticipation/release/recovery, timing và chỗ gắn
vũ khí. Xem ở 1x và khi phát animation; diagnostics chỉ báo chỗ cần xem, không tự xác nhận chất lượng.
Với `motion`, dùng tốc độ nhân vật thật trong game; mặc định 24 px/s chỉ để kiểm tra ban đầu.
`Pixelbolt` export thời lượng frame riêng; metadata Sprite Lab giữ nguyên bằng `durations_ms`. `art run` tự
chọn nguồn `.poses.json` nếu sprite có file đó; sprite dùng `gen.py` tiếp tục theo pipeline hiện tại.

## Quy trình (đủ các bước mới được báo xong)

1. **Chốt spec**: kích thước (16/24/32/48/64; nhân vật cao thì chừa khoảng trống phía trên cho nhảy), palette
   4–16 màu, hướng nhìn (mặc định quay phải), **điểm neo** (nhân vật đứng: giữa hai bàn chân trên mặt đất;
   vật bay: tâm thân; đạn/giọt: đầu va chạm), danh sách animation với số frame/fps/loop. Mơ hồ thì chọn mặc
   định và nói rõ. Tên animation dùng bộ chuẩn để lab và game hiểu: `idle`, `walk`/`run`/`fly`/`move`,
   `jump`, `attack`, `spell`, `hurt`, `death`.
2. **Vẽ silhouette trước** bằng ASCII map trong `gen.py` (`from_rows`, `outline`), rồi mới thêm chi tiết.
3. **Render**: `gamekit art run <tên>`. Lệnh này dừng nếu thiếu `<tên>.json`, neo nằm ngoài khung, hoặc
   animation không liền nhau. `gen.py` gọi `write_anim_meta(...)` (đã có sẵn trong mẫu); sprite một animation
   có thể dùng `write_meta`. **Nhân vật đứng trên đất** gọi `write_anim_meta(..., ground=True)`, đánh dấu
   animation rời đất bằng `"airborne": True` (nhảy). Khi đó mọi frame còn lại phải có hàng pixel thấp nhất
   (kể cả viền) nằm ngay trên điểm neo; lơ lửng hay lún đều bị `art run` từ chối (bài học 2026-11-16).
   Nhân vật nhỏ kiểu tối giản dựng nhanh bằng `sprite-lab/lib/minifig.py` (tư thế bằng số, tỉ lệ giữ nguyên;
   xem `sprites/swordsman/gen.py`, `sprites/mage/gen.py`).
4. **Xem tĩnh**: mở `sprite-lab/sprites/<tên>/preview.png` bằng công cụ đọc ảnh của agent. Mỗi animation một
   hàng. Nhiều agent không đọc được GIF động; `<animation>.gif` là cho người xem. Sửa, lặp 2–3 vòng.
5. **Thử sheet**: `gamekit art shot <tên> sheet` rồi xem ảnh. Mọi animation chân/neo nằm trên đường đất,
   khung không cắt mất hình (mũ khi nhảy, vũ khí khi vung).
6. **Thử di chuyển**: `gamekit art shot <tên> move` rồi xem ảnh lưới. Đạt khi: lật hướng không làm sprite
   xê dịch, đi/chạy có nhịp, nhảy có độ cao và bóng hợp lý, đòn đánh/phép/trúng đòn đọc được.
7. **Test**: `gamekit art test` (unit `SpriteSheet`/`SpriteAnchor` + integration mọi sprite trong lab).
8. **Commit** ở repo gốc (`sprite-lab/` thuộc repo gốc): `gen.py`, strip, json, png, preview, gif.
9. **Đưa vào game** (chỉ khi game cần): `gamekit art promote <tên> <game>` → vẽ bằng `SpriteSheet` trong code
   game → `gamekit test <g>` + `gamekit shot <g>` và **xem ảnh** → commit repo game.

Không báo "xong" khi chưa xem `preview.png`, ảnh `sheet` và ảnh `move`.

## Hiệu ứng đòn đánh / phép (hitbox)

> Bài học 2026-11-16 (`LESSONS.md`): đòn mặc định của kiếm sĩ dùng một sóng chém lớn không hợp kiếm ngắn, và
> tầm đánh gõ tay trong data game không khớp với hình.

- **Vẽ theo vũ khí**: đòn mặc định của một nhân vật có cỡ bằng tầm vũ khí của chính sprite đó (tay + lưỡi);
  sóng chém bay xa, vùng nổ lớn là nâng cấp, không phải đòn đầu.
- **Neo = điểm xoay** của hiệu ứng (vai/tay với vệt chém, tâm với vòng xoáy), không phải tâm canvas tùy tiện.
- **Mọi hiệu ứng liên quan đến chiến đấu phải có `hitbox` ngay khi thiết kế** (đòn đánh, projectile, vụ nổ,
  AOE, vùng gây/nhận hiệu ứng…) để game dùng trực tiếp, không phải thiết kế lại: truyền spec
  `{"shape": "rect"|"arc"|"circle", "center": [x, y], "active": [frame_đầu, frame_cuối], "dir_deg": d}` vào
  `export(...)`/`write_anim_meta`. Chọn hình theo **hình dạng thực tế** của animation: `rect` cho tia/cột/vệt
  thẳng kéo dài, `arc` cho quét/chém hình quạt, `circle` cho vùng tròn/nổ đều. Vùng đo từ pixel frame active
  (alpha ≥ 96, quầng mờ không tính) bởi `fit_hitbox`; `gamekit art run` từ chối hitbox lệch với pixel. Xem
  hitbox trên ảnh `gamekit art shot <tên> sheet` (đỏ = frame gây sát thương) và trên web viewer (bật "Hitbox").
- **Thân (hurtbox) của nhân vật/quái** cũng đo từ pixel: `export(..., body="move")` hoặc
  `write_anim_meta(..., body="idle")` ghi `"body"` (tâm = trọng tâm pixel đặc, bán kính = hình tròn cùng diện tích);
  `art run` từ chối `body` lệch với pixel; ảnh `sheet` vẽ thân màu xanh lá.
- Trong game: vùng trúng lấy bằng `SpriteHitbox.of(sheet, anim, điểm_vẽ, tỉ_lệ, lật)`, thân bằng
  `SpriteHitbox.body(sheet, điểm_vẽ, tỉ_lệ, lật)`, cùng điểm và tỉ lệ với lúc vẽ; data game chỉ chứa hệ số
  (sát thương, `area`), **không** chứa bán kính/tầm đánh/tâm thân gõ tay.

## Nhân vật: góc nhìn, đòn đánh, lớp (mặc giáp)

- **Góc nhìn theo quyết định của game**, ghi trong design của game. Bách Ải (2026-11-16): chỉ góc ngang, trái =
  lật; nhân vật chỉ có `idle`, `run`, `hurt`, `death`. Game cần thêm góc thì dùng `<anim>_down` / `<anim>_up`,
  cùng tỉ lệ, cùng neo, cùng đường đất. Ở góc trước/sau, tay giơ cao đi **cạnh** đầu, được vẽ trước đầu, không
  cắt ngang mặt/tóc; vũ khí luôn nối liền với bàn tay (bài học `attack_up`).
- **Đòn đánh không vẽ vào thân**: vệt chém, vụ nổ là sprite hiệu ứng riêng có hitbox. Vẽ cả hai thì game hiện hai
  vệt.
- **Nhân vật mặc được đồ thì vẽ theo lớp**: dựng bằng `minifig.draw_layers` và xuất bằng
  `sheet.export_layered(...)`. Kết quả gồm `layers/<lớp>_strip.png` (không viền), `"layers"` và `"outline"` trong
  json, `layers.png` để duyệt. `check_layers` (trong `art run`) bắt các lớp ghép lại + viền phải trùng từng pixel
  với strip. Thứ tự lớp và ô trang bị: `minifig.LAYERS` (đầu: `hair`, ngực: `torso`/`arm_*`/`neck`, chân: `leg_*`,
  giày: `boot_*`, tay: `hand_*`, vũ khí: `weapon*`, áo choàng: `cape_back`). Đồ mặc vẽ lại đúng các lớp của ô bằng
  **cùng tư thế** của nhân vật; game ghép bằng `SpriteSheet.compose_layers({lớp: texture})` (viền sau khi ghép).
- Xem **phóng to từng frame** của mỗi animation mới (preview cả sheet quá nhỏ để thấy lỗi tay/vũ khí).

## Quy tắc pixel art

- **Hình đặc trưng vẽ bằng bản đồ pixel tay** (`from_rows` hoặc danh sách chuỗi): nón, mũ, đầu vũ khí, khuôn
  mặt, biểu tượng. Công thức (vòng lặp co giãn, lệch theo k²…) chỉ dùng để đặt vị trí và tạo chuyển động; dựng
  hình dáng bằng công thức cho ra bậc thang lởm chởm (bài học 2026-11-16: nón pháp sư "méo xẹo"). Cần biến thể
  (gió, nghiêng) thì vẽ thêm một bản đồ, đừng uốn bằng công thức.
- **Đường chéo đặc (lưỡi kiếm, vệt chém…) điền theo từng cột**: với mỗi cột `x`, tính tâm `y` rồi tô một
  đoạn `y` liên tiếp; vòng lặp kiểu `(x+t, y-t)` chỉ cho pixel chạm góc → nhìn như caro/đứt gãy (bài học
  2026-11-16: sword/greatsword). Guard phải **vuông góc** với trục lưỡi, cán/pommel **cùng trục** với lưỡi.

- Không anti-alias, không gradient mịn; dùng màu phẳng và banding.
- 1 pixel = 1 đơn vị thiết kế; scale nguyên, nearest.
- Silhouette phải đọc được ở 1x; outline tối 1px hoặc selective outline.
- Animation: 4–8 frame cho idle/loop, 6–10 cho walk/run; đổi 1–2 pixel mỗi frame; neo cố định qua mọi frame.
- Nền trong suốt (`RGBA`), không viền quanh cả canvas.

## Godot 4.7

- Vẽ bằng addon dùng chung `addons/gamekit/sprites/`:
  `SpriteSheet.load_dir(dir, name)` rồi `sheet.draw(self, anim, t, point, scale, flip_h)` trong `_draw()`.
  Bên dưới là `SpriteAnchor.dest_rect`: **không** căn theo tâm canvas, **không** tự tính lại rect khi lật
  bằng chiều rộng âm (Godot giữ vùng vẽ, chỉ lật texture).
- Pixel art cần lọc Nearest: `rendering/textures/canvas_textures/default_texture_filter=0` (game do `gamekit
  new` tạo và lab đã có). Thiếu nó, sprite bị nhòe khi phóng to.
- Export: preset phải gói `assets/sprites/*.json` (template của gamekit đã có).

## Môi trường đã kiểm chứng

- `libresprite` 1.3 ở `~/.local/bin/libresprite` (GPL-2.0). Bản 1.3 **không có MCP/HTTP/`--set`**; script
  headless chỉ vẽ được một frame, nên animation làm bằng Python. Lỗi JS in `Error:` nhưng exit code vẫn 0,
  nên luôn kiểm tra file output.
- Pillow 10.2 có sẵn; **không có numpy**.

## Không làm

- Không tạo hay thử sprite trong thư mục game; không thêm cờ xem thử sprite vào code của game.
- Không gõ số frame, fps, neo vào config của game: chúng nằm trong `<tên>.json` do `gen.py` sinh ra.
- Không dùng dịch vụ ảnh trả phí, không gửi art lên mạng.
- Không sửa `templates/` hay `tools/lpc-generator/` (clone upstream).
- Không ghi đè sprite đã promote khi chưa hỏi; sửa trong lab rồi promote lại.
- Không bỏ qua commit (`AGENTS.md`, "Quy tắc commit"): lab ở repo gốc, bản promote ở repo game.
