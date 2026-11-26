# Màn tiêu đề: thiết kế lại (lần 2)

Người dùng 2026-11-26: "màn tiêu đề hiện tại trên web bỏ hết đi, thiết kế lại". Ba bản web cũ (cổng ải, dải băng,
cuộn giấy, có trạng thái "nhấn phím bất kỳ") đã xoá; màn trong game: `games/bach-ai/production/ui/00-title.png`.

## Bản cũ (tránh lặp lại)

- Trong game: logo "BÁCH ẢI" vàng ở giữa trên, "Vượt trăm ải" dưới; hai nhân vật Kiếm sĩ / Pháp sư đối xứng trên bệ đá
  vòng rune; một cột 4 nút xanh đen viền vàng ở giữa (Tiếp tục đỏ có dòng phụ); nền cỏ tối; phiên bản góc trái.
- Web cũ: A cổng đá (menu trong vòm), B dải băng ngang dưới, C cuộn giấy; cả ba giữ hai nhân vật trên bệ, đồng cỏ đêm.

## Tham khảo

- GamesRadar, giá trị của menu chính (https://www.gamesradar.com/the-hidden-value-of-video-game-main-menus-and-the-design-secrets-that-compel-you-to-hit-play):
  menu hợp không khí của game; Spec Ops: The Line đổi cảnh menu theo tiến độ câu chuyện. Học: màn tiêu đề kể tiến độ
  của người chơi. Quyết định: hướng B vẽ đường qua 100 ải và đánh dấu ải đang tới.
- Bình luận itch.io về menu 3 nút (https://itch.io/post/10087981): ít nút, bớt gánh nhận thức. Học: chỉ 4 mục, một mục
  chính. Tránh: thêm mục (album, nhiệm vụ…) ở tiêu đề; chúng ở Sảnh.
- Devlog Cogmind (https://www.moddb.com/news/anatomy-of-an-ascii-title-screen): màn tiêu đề vẫn đáng giữ dù không có
  chức năng, vì nó đặt không khí. Quyết định: hướng C chỉ là một cảnh và chữ.
- Không tìm được phân tích menu riêng của Slay the Spire, Hades, Dead Cells (tìm 2026-11-26).

## Ba hướng (Design Lab: `#bach-ai/title/<0|1|2>`, ảnh `shots/title-*.png`)

| Hướng | File | Ý chính |
|---|---|---|
| A. Bìa sổ | `screen-title-cover.html` | bìa da của chính cuốn sổ hành trình ở Sảnh: tên dập vàng, huy hiệu nhân vật, khoá cài; menu là 4 dải đánh dấu trang thò ra mép phải; Enter "mở sổ" vào Sảnh |
| B. Bản đồ trăm ải | `screen-title-map.html` | bản đồ vẽ tay, đường qua các ải (ải đã qua đỏ), nhân vật đứng ở ải đang tới; tên trong ô khung; menu là ô Chú giải |
| C. Hoàng hôn trước trận | `screen-title-dusk.html` | cảnh rộng: trời hoàng hôn, các dãy cổng ải xa dần, nhân vật trên đồi; tên lớn lệch trái; menu chữ ngang, ←/→ |

Cả ba bỏ: hai nhân vật trên bệ, cột nút giữa, cổng / dải băng / cuộn giấy của bản cũ.
