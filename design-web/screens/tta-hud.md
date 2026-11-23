# HUD trong trận — Thất Tinh Ấn (bản thiết kế trên web)

Màn chơi chính (Làng Hạc / Đồi sim). Game mobile 640×360 ngang; bản thử 1280×720 = ×2. Cảm ứng là input chính.
File: `design-web/screen-tta-hud.html` (`?state=dialog` hoặc phím `K` để bật hộp thoại).

## Tham khảo

| Nguồn | Lấy | Tránh |
|---|---|---|
| [booba-game: mobile platform UX](https://booba-game.pages.dev/mobile-platform-ux) (dẫn Diablo Immortal) | Joystick trái + nút kỹ năng phải là chuẩn của ARPG mobile; kỹ năng là một chạm rời | — |
| [itch.io devlog: HUD prefab layout changes](https://itch.io/devlog/1111215/hud-prefab-layout-changes.amp) | Thông báo/tracker không được nằm trong vùng joystick (dễ đè nhau) | Đặt hộp thông báo góc dưới trái |
| [Throne and Liberty UI/HUD guide](https://metaforge.app/throne-and-liberty/ui-hud-guide-throne-and-liberty), [RIFT user interface](https://www.gamepressure.com/rift/user-interface/z54fd7) | Chân dung + HP/MP gắn liền ở góc trên trái | — |
| [Ocean View Games: mobile UI for complex games](https://oceanviewgames.co.uk/blog/posts/mobile-ui-design-complex-games), [MIR4 interface](https://gameplay.tips/guides/mir4-interface-guide.html) | Neo mọi khối vào mép/góc để màn rộng (19,5:9) không đè; khu địa danh góc trên phải, nhiệm vụ ngay dưới | Khối trôi giữa màn |

**Quyết định:** trên trái = chân dung + HP + KI + Sức mạnh (thanh tới ngưỡng kế), dưới là Linh khí/Vàng và hàng
7 ấn (ấn đã có tô vàng). Trên phải = tên vùng + nhiệm vụ đang làm. Dưới trái = joystick luôn hiện mờ (người mới
biết chỗ chạm). Dưới phải = Đánh (to nhất, đỏ), Nói (ngọc), Chỉ số (vàng). Hộp thoại ở giữa đáy, giữa joystick
và cụm nút, có bảng tên người nói.

## Bố cục (toạ độ 1280×720; game chia đôi)

- Chân dung 372×104 tại (24, 24); khung mặt 84; thanh HP/KI 250×18; chữ số căn giữa dọc trong thanh.
- Tài nguyên cao 38 tại y 140; hàng ấn 318×44 tại y 190 (7 hình thoi 24 px).
- Tên vùng 300×48 và nhiệm vụ 300×80, neo mép phải 24 px.
- Joystick Ø168 tâm cách trái 168 / đáy 156. Nút: Đánh Ø132, Nói Ø88, Chỉ số Ø88, neo mép phải/đáy.
- Hộp thoại 600×132, cách đáy 28, x 300.

## Ảnh

`shots/tta-hud-normal.png`, `shots/tta-hud-dialog.png`.
