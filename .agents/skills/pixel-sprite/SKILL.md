---
name: pixel-sprite
description: >
  Thiết kế sprite pixel art cho game trong workspace này: nhân vật, kẻ địch,
  icon, vật phẩm, hiệu ứng, animation và sprite sheet. Dùng khi người dùng nhờ
  vẽ/sửa sprite, làm art không phải nhân vật LPC, tạo animation 2D, hoặc làm
  việc với LibreSprite/.ase. English triggers: pixel art, sprite, spritesheet,
  animation frames, LibreSprite, Aseprite, game art, tileset, icon.
---

# Pixel sprite (game-studio)

Agent tự thiết kế bằng generator + vòng lặp nhìn ảnh. Không điều khiển GUI.
LibreSprite dùng để con người chỉnh tay và để chuyển `.ase` ↔ `.png`.

## Môi trường đã kiểm chứng

- `libresprite` 1.3 ở `~/.local/bin/libresprite` (GPL-2.0, AppImage).
- Pillow 10.2 có sẵn; **không có numpy**.
- v1.3 **không có MCP/HTTP/`--set`/`tools.*`/`app.isHeadless`**. MCP server
  (`data/scripts/mcp-server.js`) chỉ có trên master sau v1.3 — đừng cấu hình
  MCP cho bản 1.3.
- Script headless v1.3 chỉ vẽ được một frame; animation làm bằng Python.
- Lỗi JS in `Error:` nhưng exit code vẫn 0 → luôn kiểm tra file output.

## Lệnh

```sh
gamekit art new <game> light-mote --size 24   # scaffold gen.py
gamekit art run <game> light-mote             # render PNG + preview + GIF
gamekit art ase <game> light-mote             # PNG -> .ase (cho người chỉnh)
gamekit art open <game> light-mote            # mở .ase trong LibreSprite
```

Trong thư mục game có thể bỏ `<game>`:
`gamekit art run light-mote`.

## Cấu trúc file

```text
games/<g>/assets/source/sprites/<name>/   # .gdignore: không vào bản export
  gen.py                                   # generator cần sửa
  preview.png, anim.gif, <name>.ase        # để xem/chỉnh tay
games/<g>/assets/sprites/custom/<name>/   # Godot import
  <name>.png                               # frame chính
  <name>_strip.png                         # dải animation (nếu nhiều frame)
```

`gen.py` tự tìm `tools/gamekit/pipeline/spritekit.py` bằng cách đi ngược lên
workspace. Không copy helper vào từng game, không hard-code đường dẫn tuyệt đối.

## Quy trình

1. **Chốt spec**: kích thước (16/24/32/48/64), palette 4–16 màu, số frame, fps,
   hướng nhìn, anchor (chân giữa), nền trong suốt. Mơ hồ thì chọn mặc định và
   nói rõ.
2. **Vẽ silhouette trước** bằng ASCII map trong `gen.py`:

   ```python
   from spritekit import from_rows
   rows = [
       "....####....",
       "..########..",
       ".##########.",
       "..########..",
       "....####....",
   ]
   c = from_rows(rows, {"#": "#ffd34d"})
   c.outline("#5a3300")
   ```

3. **Chạy và nhìn**: `gamekit art run <g> <name>`, rồi dùng công cụ đọc ảnh của agent (Read, read, view…)
   mở `preview.png` (ảnh tĩnh, phóng to, có lưới). Nhiều agent không đọc được GIF động: xem các frame trong
   `preview.png`, còn `anim.gif` là cho người xem. Sửa, lặp 2–3 vòng.
4. **Kiểm tra trong game**: thêm PNG vào `Sprite2D`/`AnimatedSprite2D` hoặc
   `_draw`, chạy `gamekit test <g>` + `gamekit shot <g>` rồi xem ảnh.
5. **Bàn giao**: PNG trong `assets/sprites/custom/`; `.ase` trong `assets/source/`
   nếu người dùng muốn chỉnh tay.

## Quy tắc pixel art

- Không anti-alias, không gradient mịn; dùng màu phẳng và banding.
- 1 pixel = 1 đơn vị thiết kế; scale nguyên, nearest.
- Silhouette phải đọc được ở 1x; outline tối 1px hoặc selective outline.
- Animation: 4–8 frame cho idle/loop, 6–10 cho walk; đổi 1–2 pixel mỗi frame,
  giữ chân/tâm cố định.
- Nền trong suốt (`RGBA`), không viền quanh cả canvas.

## Godot 4.7

- Pixel art cần lọc Nearest. Game do `gamekit new` tạo đã có sẵn
  `rendering/textures/canvas_textures/default_texture_filter=0`; game cũ thì thêm dòng này vào `project.godot`
  (hoặc đặt `texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST` trên node). Thiếu nó, sprite bị nhòe khi phóng to.
- Bật `rendering/2d/snap/snap_2d_transforms_to_pixel` nếu sprite bị nửa pixel.
- File PNG trong `assets/sprites/` được Godot tự import; không cần `.tres` cho
  sprite đơn, dùng `AnimatedSprite2D` + `SpriteFrames` nếu có animation.

## Không làm

- Không dùng dịch vụ ảnh trả phí, không gửi art lên mạng.
- Không sửa `templates/` hay `tools/lpc-generator/` (clone upstream).
- Không ghi đè sprite/credits hiện có khi chưa hỏi.
- Không bỏ qua commit: theo "Quy tắc commit" trong `AGENTS.md` ở gốc workspace, commit `gen.py`, PNG và
  `.ase` (nếu có) vào repo của game ngay khi sprite đạt.
- Không báo "xong" khi chưa mở ảnh preview và ảnh chụp trong game.
