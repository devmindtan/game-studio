---
name: art-reference
description: >
  Tìm reference free trước khi thiết kế sprite, hiệu ứng, icon, nhân vật: bộ Lospec
  palette trong `art-refs/palettes/` và LPC trong `tools/lpc-generator/` + các site free
  khác (Kenney, OpenGameArt). Dùng khi người dùng yêu cầu vẽ art mới, đổi style, hoặc
  không nhớ ý tưởng; đừng tạo art từ con số 0 khi có thể tham khảo.
  English triggers: art reference, find inspiration, look up sprite, palette for art,
  choose a color palette, reference for effect.
---

# Art reference

Tránh thiết kế mò tốn token: trước khi vẽ một sprite mới, **xem tham khảo** — palette, bố cục khung, cách
layer outline — rồi tự vẽ lại bằng `gen.py` trong Sprite Lab. Không bao giờ sao chép đúng pixel của
asset người khác; đây chỉ là **tham chiếu ý tưởng**.

## Palettes miễn phí (đã tải 27 bộ)

`art-refs/palettes/*.json` + `art-refs/palettes/index.json` (tên, tác giả, số màu). Dùng để chọn bảng
màu; xem cả danh sách đầy đủ trong `ATTRIBUTIONS.md`. Một vài bộ đáng chú ý:

| id | phù hợp |
|---|---|
| `cc-29` | 29 màu, đa dụng cho mọi sprite pixel |
| `dawn-32` | 32 màu, retro-ish, bền cho mọi sprite pixel |
| `resurrect-64` | 64 màu, đô thị/công trình/chi tiết dày — không dùng cho sprite 16 px |
| `magicolor-16` | 16 màu, nature/earth — slime, rừng, đất đá |
| `afr-32` | 32 màu, đất/rừng/ẩm — các vùng thân thiện ánh sáng |
| `aragon16` | 16 màu, cảnh quan nắng/ngày |
| `wheat-field` | 10 màu, ấm, champ/lúa |
| `verdant-valley` | 24 màu, thung lũng xanh đậm |
| `mushroom` | 14 màu, đỏ/tím/nâu — nấm, vật phẩm phép, boss rùng rợn |
| `frozen-fire` | 14 màu, nắm lạnh/nóng — đánh mạnh vào ice vs fire skills |
| `st-8-phoenix` | 8 màu, kim loại/phượng hoàng — fire/burn effects |
| `sunraze` | 14 màu, đỏ sunset/destruction — dark energy |
| `sunfall` | 10 màu, cam/đỏ harsh torchlight — lửa, đèn |
| `foxfire` | 4 màu, tím/cam/trắng — wisp, ma lửa |
| `pola5` | 5 màu, băng mono — frost tiles |
| `icywitch` | 6 màu, teal/vàng băng — boss băng |
| `blue-glass` | 8 màu, đá xanh/băng — ice wall |
| `dead-ice` | 4 màu, xanh glaciar/stone — dark tank |

Ví dụ tra palette bằng shell (không cần mở browser):

    python3 -c "import json; d=json.load(open('art-refs/palettes/cc-29.json')); print(d['colors'])"

## LPC (nhân vật)

`tools/lpc-generator` đã chứa toàn bộ sprite sheet LPC (`spritesheets/*.png`) + `CREDITS.csv`. Cách dùng:

- Mở các sheet trong `body/`, `torso/`, `legs/`, `hair/` để hiểu cách layer chân/eo/thân/mũi.
- Đọc `CREDITS.csv` khi dùng: nhân vật LPC trong game **bắt buộc** credits (xem `gamekit sprites`).
- Không mở nhầm các sheet có license GPL (game của mình là private/player-owned, theo từng dự án).

## Kenney (xem, không tải)
Kenney assets (CC0): `kenney.nl/assets` — tìm "particles", "explosion", "UI", "pixel". Khi chép tay từ preview:

- Chọn **1-2 khung mẫu** để học cách nhịp (anticipation → burst → fade), không copy nguyên sprite.
- Không tải file zip vào repo khi chưa cần — tránh lưu hàng chục MB asset không dùng.

## Kết quả cuối

Sau khi tham khảo, bằng chứng token tiết kiệm là: `gen.py` của sprite mới có comment nêu palette và
lý do bố cục (VD 'lightning: 6 frame, mỗi bolt 2-3 đòn, palette resurrect-64, gradient từ #f5f3ff -> #7dd3fc').
