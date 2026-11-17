# External art sources (all free/CC0 or OGA-BY)

Danh sách nguồn tham khảo được phép dùng cho thiết kế art. Các nguồn này **không được tải hàng loạt
vào repo** — chỉ dùng để tra cứu ý tưởng, hoặc tải ít asset CC0 về dùng ngay cho effects/items/props
(tên/không gian/quy ước ghi credit). Tất cả phải là **miễn phí sử dụng thương mại không tuần tự**.

> **Quy tắc chung**: đọc tham khảo → tự tạo art mới bằng gen.py trong Sprite Lab → credit nếu dùng trực tiếp.
> Không chép nguyên sprite từ bất kỳ nguồn nào. LPC: luôn có credits (`gamekit sprites` kiểm tra).

## Kenney (CC0) — effects, items, GUI
- https://kenney.nl/assets — CC0; dùng cho **items (rương, chìa khoá, tiền)**, **project/effects** làm mẫu bố cục.
- Tìm “particles”, “explosion”, “ui”, “icons”; dowload từng gói nếu cần.
- Khi đã dùng trong game: ghi tên gói + tác giả; CC0 không bắt buộc credit nhưng nên ghi `credits.csv`.

## Lospec (CC0 / Creative Commons cho community) — bảng màu
- API: `https://lospec.com/palette-list/<slug>.json` — tải index này qua curl, không cần login.
- Bản quyền: các palette do cộng đồng đăng là public domain hoặc CC0; đọc kỹ mỗi trang palette trước khi redistribute.
- Bộ đã tải tại `art-refs/palettes/` (27 palettes), xem `ATTRIBUTIONS.md`.

## OpenGameArt (OGA-BY / CC-BY-SA / GPL)
- https://opengameart.org — lớn nhưng license hỗn hợp; chỉ dùng để nghiên cứu (bộ chân dung LPC đã nằm trong `tools/lpc-generator`).
- Không tự nó tải hàng loạt; OGA-BY yêu cầu ghi công tác giả nếu dùng trong sản phẩm.

## Universal LPC Spritesheet (đã có trong repo)
- `tools/lpc-generator/` — MIT; sprites bên trong: OGA-BY / CC-BY-SA / GPL.
- Dùng khi nhân vật; `gamekit sprites <g>` kiểm tra credits bắt buộc.

## CC0 texture/material websites
- https://freestocktextures.com / https://textures.com (CC0 subset) — không dùng trực tiếp; chỉ tham khảo chất liệu.
