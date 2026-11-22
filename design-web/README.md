# Design Lab: thiết kế màn hình game trên web

Nơi dựng và soát **màn hình game** trước khi viết vào Godot. Mỗi màn là một trang HTML cố định
**1280×720 (16:9)**, chạy trong khung game: không cuộn, không thanh điều hướng web, bàn phím là
input chính. Đây là bản thiết kế để chốt bố cục/màu/chữ, **không phải** giao diện sẽ ship thẳng.

```text
design-web/
├── index.html          Design Lab: khung soát, đổi màn/biến thể, lưới, vùng an toàn
├── screen-title.html   Màn chờ + màn tiêu đề BÁCH ẢI (bản thiết kế)
├── screen-title.css    Bố cục, màu, chuyển động của màn hình
├── screen-title.js     Bàn phím, focus, vòng rune, toast
├── screens/title.md    Đặc tả màn hình + nguồn tham khảo
├── fonts/              VT323 (OFL), phủ đủ tiếng Việt
└── vendor/             tool/asset tham khảo, KHÔNG commit (setup.sh tải về)
```

## Chạy

```sh
design-web/setup.sh          # lần đầu: tải font + clone tool tham khảo (vendor/)
design-web/serve.sh          # http://localhost:8770/design-web/index.html
```

Mở `index.html`, bấm vào khung game rồi dùng:

- `↑` `↓` (hoặc `W` `S`): đổi nút đang chọn
- `Enter` / `Space`: xác nhận
- `Esc`: từ menu về màn chờ
- Ở màn chờ: phím bất kỳ hoặc bấm chuột để vào menu

## Quy ước thiết kế (game, không phải web)

| Làm | Tránh |
|---|---|
| Khung 16:9 cố định, mọi thứ theo px | Bố cục responsive co giãn như trang web |
| Bàn phím/gamepad là input chính, có focus rõ | Chỉ hover/click, không thấy đang chọn gì |
| Chữ ≥ 18 px trong khung 1280×720 | Chữ 12–14 px kiểu web |
| Panel vuông, viền dày, bevel, họa tiết góc | Card bo tròn, bóng mờ mềm, gradient web |
| Một hành động chính nổi nhất | Nhiều nút ngang hàng, menu nhiều tầng |
| Chuyển cảnh ngắn, dứt khoát | Animation dài, parallax nặng |
| Ảnh pixel `image-rendering: pixelated` | Scale lẻ làm nhòe pixel |

Sau khi chốt: viết lại vào `games/<g>/src/...` theo `production/ui/screens.json`, rồi
`gamekit ui-shots <g>` và soi ảnh ở độ phân giải thật.

## Tool/asset tham khảo (`vendor/`, CC0/CC-BY)

`setup.sh` clone về, không commit (xem `.gitignore`):

| Thư mục | Nguồn | Giấy phép | Dùng để |
|---|---|---|---|
| `vendor/icons` | [game-icons/icons](https://github.com/game-icons/icons) | CC BY 3.0 | icon SVG cho nút/HUD; game đã dùng game-icons.net |
| `vendor/kenney-uipack` | [lpfd/kenney-uipack](https://github.com/lpfd/kenney-uipack) | CC0 (Kenney) | tham khảo panel/button 9-slice, không copy thẳng |
| `vendor/kenney-ui-audio` | [Calinou/kenney-ui-audio](https://github.com/Calinou/kenney-ui-audio) | CC0 (Kenney) | tiếng hover/click cho bản thử tương tác |

Font **VT323** (`fonts/`) lấy từ [Google Fonts](https://fonts.google.com/specimen/VT323),
giấy phép OFL, có subset tiếng Việt (đã kiểm `ế ụ ậ Ả ư ợ đ`).

## Thêm màn hình mới

1. Chép `screen-title.html/css/js` thành `screen-<tên>.*`, sửa nội dung.
2. Thêm mục vào danh sách màn trong `index.html`.
3. Viết `screens/<tên>.md`: mục tiêu, trạng thái, bố cục, màu/chữ, phím, **## Tham khảo** (≥ 2 nguồn
   game cùng thể loại, ghi rõ học gì / tránh gì / quyết định).
4. Chụp 1280×720 ở từng trạng thái, soi từng vùng ×2 trước khi chốt.
