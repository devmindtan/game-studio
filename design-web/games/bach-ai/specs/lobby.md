# Sảnh (Chuẩn bị): thiết kế lại

Người dùng 2026-11-26: thiết kế lại giao diện sảnh và menu, "thiết kế lại" = một hướng khác hẳn bản cũ (skill
`ui-redesign`). Màn trong game: `01-lobby` (`games/bach-ai/production/ui/01-lobby.png`).

## Bản cũ (tránh lặp lại)

- Bố cục: nhân vật trên bệ rune bên trái, một bảng thông tin lớn bên phải (4 ô chỉ số, nội tại, chiêu khởi đầu, bộ
  chiêu, mốc cấp), tiêu đề "Chuẩn bị" góc trái trên.
- Điều hướng: hàng 7 nút icon vuông ở góc phải trên + 3 nút lớn ở đáy (Cây kỹ năng, Trang bị, Chọn ải).
- Màu / khung: panel xanh đen viền vàng, nút đỏ cho hành động chính, nền cỏ xanh.
- Font: sans-serif của Godot theme; chữ gợi ý phím ở đáy.

## Tham khảo

- Towerborne, Belfry (https://news.xbox.com/en-us/2024/06/28/towerborne-belfry): sảnh là một nơi có nhân vật / công
  trình thay cho các nút. Học: mỗi mục là một vật trong cảnh. Tránh: đi bộ tới từng nơi (chậm). Quyết định: hướng A
  chọn vật bằng ←/→, không đi bộ.
- Devlog sảnh dark-fantasy (https://www.indiedb.com/news/hub-update-preview2): menu dễ dùng, đẹp, điều khiển được cả
  tay cầm lẫn chuột/bàn phím. Học: mọi mục có focus rõ, một phím xác nhận. Quyết định: cả 3 hướng đi bằng phím.
- Ý niệm menu kiểu Dark Souls (https://www.behance.net/gallery/170479815/Tarnished-UI): chữ điều hướng không chân,
  trang trí bằng khung. Học: danh sách chữ lớn, ít khung. Quyết định: hướng C chỉ có chữ và ánh sáng.
- Không tìm được ảnh / phân tích sảnh của Vampire Survivors và Soulstone Survivors (tìm 2026-11-26).

## Ba hướng (web: `screen-lobby-*.html`, ảnh: `shots/lobby-*.png`)

| Hướng | File | Ý chính |
|---|---|---|
| A. Trại lửa | `screen-lobby-camp.html` | cả màn là cảnh trại đêm; mỗi mục là một vật trên cọc gỗ (lều, cây, bàn bài, đền, bảng tin, rương, bàn bản đồ); ←/→ chọn, biển gỗ ở đáy giải thích; nhân vật ngồi cạnh lửa |
| B. Sổ hành trình | `screen-lobby-journal.html` | một cuốn sổ mở trên bàn gỗ: trang trái là nhân vật + chỉ số viết tay, trang phải là "Mục lục" các chương; con dấu sáp "Lên đường" |
| C. Tối giản | `screen-lobby-stark.html` | nền đen đỏ thẫm, danh sách chữ lớn bên trái (mục chọn sáng lên, có một dòng mô tả), nhân vật to được chiếu sáng bên phải |

Cả ba bỏ: panel xanh đen viền vàng, hàng nút icon góc phải trên, bệ rune.
Bước kế: người dùng chọn hướng → áp cho các màn menu còn lại → port sang Godot → `gamekit ui-shots`.
