# Design Lab: thiết kế màn hình game trên web

Nơi dựng và soát **màn hình game** trước khi viết vào Godot. Mỗi màn là một trang HTML cố định
**1280×720 (16:9)**, chạy trong khung game: không cuộn, không thanh điều hướng web, bàn phím là
input chính. Đây là bản thiết kế để chốt bố cục/màu/chữ, **không phải** giao diện sẽ ship thẳng.

Dùng chung cho **mọi game** của workspace (người dùng 2026-11-26):

```text
design-web/
├── index.html          Design Lab: chọn game → màn → hướng, xem trong khung 1280×720, lưới / vùng an toàn
├── games.json          danh sách game có màn thiết kế
├── fonts/              VT323 (OFL), phủ đủ tiếng Việt, dùng chung
├── vendor/             tool/asset tham khảo, KHÔNG commit (setup.sh tải về)
└── games/<slug>/       một thư mục cho mỗi game
    ├── screens.json    các màn: id, title, spec, game_shot, views [{label, note, page, query, shot, chosen}]
    ├── screen-*.html   bản thiết kế (+ css/js), font ../../fonts/, sprite ../../../sprite-lab hoặc ../../../games/<slug>
    ├── specs/<màn>.md  đặc tả: Bản cũ, Tham khảo, các hướng
    ├── shots/          ảnh 1280×720 của từng hướng
    └── assets/         tài nguyên riêng của bản thiết kế
```

## Chạy

```sh
design-web/setup.sh          # lần đầu: tải font + clone tool tham khảo (vendor/)
design-web/serve.sh          # http://localhost:8770/design-web/  (link chia sẻ: #<game>/<màn>/<số hướng>)
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

1. Game mới: tạo `games/<slug>/` + `screens.json` (`{"screens": []}`), thêm `{"slug", "name"}` vào `games.json`.
2. Viết `games/<slug>/screen-<màn>[-<hướng>].html` (mỗi hướng một trang, hoặc một trang đọc `?variant=`).
3. Khai báo màn trong `screens.json`: mỗi hướng / trạng thái là một mục `views`; hướng người dùng chọn có `"chosen": true`.
4. Viết `specs/<màn>.md`: **## Bản cũ** (khi thiết kế lại), **## Tham khảo** (≥ 2 game cùng thể loại: học gì / tránh
   gì / quyết định), các hướng.
5. Chụp 1280×720 từng hướng vào `shots/` (Chrome headless qua `limited`), soi từng vùng ×2.
6. Đưa người dùng link Design Lab `http://localhost:8770/design-web/#<slug>/<màn>/<số>`; chưa chọn thì không port.
