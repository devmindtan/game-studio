# Bộ menu "Sổ hành trình" (thiết kế lại toàn bộ trên web)

Người dùng 2026-11-26: "thiết kế hoàn thiện hết rồi mô phỏng thử trên web rồi mới đưa vào game". Sảnh đã chọn hướng B
"Sổ hành trình" (`specs/lobby.md`), tiêu đề hướng C "Hoàng hôn trước trận" (`specs/title.md`). Mọi menu còn lại dùng
cùng ngôn ngữ, chung `journal.css` (bàn gỗ, sổ mở, dải đánh dấu là tab, mực, sổ kẻ, dấu mộc, ô phác thảo, con dấu sáp là
hành động chính) và `journal.js` (đi / quay lại trong bản mô phỏng). Dữ liệu đọc thẳng từ `games/bach-ai/assets/data`.

## Bản cũ (tránh)

Mọi menu trong game hiện dùng panel xanh đen viền vàng, nút bo, tiêu đề vàng góc trái trên, nút "Quay lại (Esc)" góc
phải trên (`games/bach-ai/production/ui/*.png`).

## Tham khảo

Như `specs/lobby.md` (sảnh là một nơi chốn / đồ vật thay nút; menu theo không khí game) và `specs/title.md` (menu ít mục,
cảnh kể tiến độ). Thêm: một ngôn ngữ cho mọi màn để người chơi không phải học lại cách điều khiển ở mỗi màn.

## Các màn

| Màn | Trang trái | Trang phải | Phím |
|---|---|---|---|
| Các cuốn sổ (nhân vật) | danh sách sổ + "Viết sổ mới" | sổ chọn: chân dung, sổ kẻ, "Dùng sổ này"; viết mới: 4 lớp (khoá "Qua ải N"), dòng tên, "Viết sổ" | ↑↓, ←→ (lớp), Enter |
| Trang bị | chân dung + ô từng chỗ mặc + chỉ số | túi đồ theo chỗ mặc (viền màu độ hiếm), món chọn: độ hiếm, hiệu ứng, so với đang mặc, "Mặc" | ←→, Q/E |
| Chọn ải | bản đồ vùng: đường qua 10 ải (đã qua đỏ, trùm to hơn) | chế độ (Thường / Vô tận / Thử thách), quái vùng, thời gian, vàng, đá, "Vào trận" | ←→, Q/E vùng, ↑↓ chế độ |
| Cây kỹ năng | cây vẽ mực (nút đã học đỏ, cấp ở góc, nét liền khi đã mở) | nút chọn: mô tả, giá Tinh hoa theo hàng, cần, "Học" | ←↑↓→ |
| Bộ thẻ | thẻ đang có (Chiêu / Chỉ số, viền màu độ hiếm, ✓ trong bộ) | bộ đang dùng 8 + 6 ô, điểm hiếm, lối vào Cây thẻ, "Dùng bộ này"; dải Bộ 1/2/3 | ←↑↓→, Q/E, Enter |
| Quay đồ | quả cầu, tỉ lệ, bảo đảm, đá; dải kệ Vũ khí / Giáp | lần quay trước, "Quay ×1" / "Quay ×10" | Q/E, ←→ |
| Nhiệm vụ | việc trong ngày: ô tick, thanh tiến độ, thưởng | tổng thưởng, "Nhận thưởng" | ↑↓ |
| Cài đặt | hình ảnh, điều khiển | âm thanh (thanh %) | ↑↓, ←→ đổi |
| Album | xem `specs/album.md` | | |
| Cây thẻ | các thẻ chiêu | cây nâng cấp của thẻ chọn (card_trees.json), điểm đã dùng, Mảnh thẻ, giá cấp kế, "Nâng" | ↑↓ thẻ, ←→ nút |
| Thử thách | danh sách (khoá "Qua ải N") | áp phích luật, ải gốc, thời gian, Tẩy Tủy Đan, "Nhận thử thách" | ↑↓, Enter |
| Quay đồ: lịch sử | (như Quay đồ) | sổ kẻ các lần quay gần nhất của kệ, tên tiếng Việt, màu độ hiếm | H |

## Mô phỏng luồng

`flow.html`: tiêu đề → Enter "Tiếp tục" → Sổ (Sảnh) → Enter một chương → màn đó; Esc quay lại màn trước; "Lên đường" →
Chọn ải → "Vào trận" → trang báo vào trận. `flow.html?path=title,lobby,equipment` mở luồng đã đi sẵn.

## Tải trận (mới, người dùng 2026-11-26: "màn hình tải trận nhẹ khi vào trận")

`screen-loading.html`: nền tối hoàng hôn phẳng, tên vùng (nhỏ, giãn chữ) + "Ải N" (font chữ của game), một vạch đứt
nét làm thanh tải với nhân vật chạy dọc theo (một strip sprite, không ảnh khác để chờ), một dòng mẹo. Khoảng 1,5 s rồi
vào trận. Nhẹ có chủ ý: không cảnh vẽ, không hiệu ứng nặng.

## Trong trận (bảng)

`screen-run-journal.html?view=levelup|pause|win|lose`: trận làm tối phía sau, một tờ giấy sổ ghim đỏ, góc gấp.
- Lên cấp: 3 "trang" thẻ (icon, tên, độ hiếm đóng dấu, loại + cấp, mô tả), dưới là Đổi (R) / Loại (X) / Bỏ qua.
- Tạm dừng: danh sách Tiếp tục / Nhân vật / Cài đặt / Bỏ trận + sổ kẻ trận (cấp, quái hạ, vàng, máu).
- Thắng / Thua: dấu mộc "VƯỢT ẢI N" (xanh) / "GỤC NGÃ" (đỏ), tổng kết + sát thương theo chiêu, "Ải tiếp theo / Thử lại"
  và "Về sổ". Trong mô phỏng: P, L, W, F đổi giữa bốn bảng.

## Luồng cập nhật

Chọn ải → "Vào trận" → Tải trận → bảng trong trận; chế độ Thử thách → Thử thách → Tải trận; Bộ thẻ → T → Cây thẻ;
Quay đồ → H → Lịch sử. Trang tải trận không nằm trong đường quay lại (Esc từ trận về Chọn ải).
