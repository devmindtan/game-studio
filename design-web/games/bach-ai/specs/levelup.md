# Lên cấp: chọn thẻ (thiết kế lại)

Người dùng 2026-11-28: "phần chọn thẻ khi lên cấp cần thiết kế lại tôi thấy cái đó chưa được".
Màn trong game: `04-level-up`, `04b-level-up-milestones`, `04d-level-up-hidden` (`src/run/run_panels.gd`).

## Bản cũ (tránh lặp lại)

- Bố cục: một tấm giấy be lớn giữa màn che gần hết trận; tiêu đề đỏ "Lên cấp N! Chọn một", hai link (Ẩn bảng H,
  Nhân vật Tab), dòng tỉ lệ độ hiếm, ba thẻ ngang bằng nhau, hàng ba nút viền đỏ (Đổi / Loại / Bỏ qua).
- Thẻ: viền mảnh màu độ hiếm, icon 40 px, tên 20 px, dòng loại · độ hiếm · Mới, lưới chỉ số trước → sau và đoạn mô tả
  cỡ 13–15 px. Mọi thông tin hiện cùng lúc trên cả ba thẻ, nên chữ nhỏ và dày đặc, khó đọc nhanh.
- Màu: giấy be, chữ nâu, đỏ son; khung chữ nhật phẳng.
- Điều hướng: ← → chọn thẻ, phím số, Enter; R / X / S cho Đổi / Loại / Bỏ qua.

## Tham khảo

- **Hades (boon)**: học: danh sách dọc, mỗi dòng một icon lớn, màu viền là độ hiếm, một hiệu ứng chính đọc ngay.
  Tránh: người chơi phàn nàn thiếu chỗ xem các boon đã có ([Steam](https://steamcommunity.com/app/1145350/discussions/2/5796774377119706726),
  [mod Improved Boon Info UI](https://thunderstore.io/c/hades-ii/p/SMarBe/Improved_Boon_Info_UI/v/1.2.0/)).
  Quyết định: hiện "Đang mang" (chiêu đã có, kèm cấp) ngay trên màn chọn (hướng A).
- **Vampire Survivors**: học: 3–4 lựa chọn, có "Mới" / cấp, nút Banish (Loại). Tránh: quá nhiều chữ, người chơi xin thêm
  icon thay chữ ([itch.io](https://itch.io/post/5671708)); chữ nhỏ trên màn lớn. Quyết định: mỗi lựa chọn chỉ một con số
  lớn (thay đổi quan trọng nhất), phần còn lại chỉ hiện cho lựa chọn đang chọn.
- **Slay the Spire / Balatro (thưởng bằng lá bài)**: học: lá bài đứng, màu lá là độ hiếm, lá đang chọn nhô lên, các lá
  khác tối đi. Tránh: chữ mô tả dài nhét trong lá. Quyết định: mô tả dài để ở dải chi tiết dưới (hướng B, C).
- Tìm Halls of Torment không ra mô tả bố cục màn chọn; không dùng.

## Vòng 1 (bỏ)

A Bảng lệnh / B Ba lá bài / C Cuộn treo: người dùng 2026-11-28 "cả 3 đều xấu ... đừng bám vào cái giấy nữa vì nó khá
xấu". Đã xoá. Tránh: giấy be, gỗ, font VT323 (game vẽ bằng DejaVu Sans).

## Vòng 2: ba hướng (design-web/games/bach-ai, chung `levelup-base.css`, `levelup-data.js`)

- **D · Ngọc ấn** `screen-levelup-gem.html`: 3 thẻ đá tối viền pixel bậc thang, viên ngọc độ hiếm phát sáng trên đỉnh,
  icon trong hốc lớn, một con số lớn; thẻ chọn nhô lên và sáng; dải chi tiết dưới. ← →.
- **E · Dải kính** `screen-levelup-glass.html`: 3 dải kính mờ ngang màn, màu độ hiếm tràn từ trái, icon 116 px tràn khỏi
  dải; dải chọn trượt ra và mở chi tiết; "Đang mang" bên phải. ↑ ↓.
- **F · Vòng quanh nhân vật** `screen-levelup-orbit.html`: trận vẫn thấy với đèn rọi quanh nhân vật; 3 huy hiệu tròn trên
  vòng phía trên nhân vật; thẻ chi tiết mở ở phía đối diện. ← →.

Font: DejaVu Sans của game (`design-web/fonts/DejaVuSans.ttf`). Dữ liệu: thẻ thật của 04-level-up (Mài kiếm, Chém kiếm)
và Đất nứt (Hiếm) của 04b.

## Vòng 3: kiểu tối cũ, làm đẹp (`screen-levelup-polish.html`)

Người dùng 2026-11-28: "tôi vẫn thích theo phong cách cũ trước khi đổi hơn, từ cái đó cải thiện hơn đẹp hơn và hiệu ứng
mượt hơn", "không phải là tấm giấy mà là trước đó nữa" (màn trước commit 6c5ff68a), "các button cần được thiết kế chỉnh
chu hơn". Giữ: bố cục (tiêu đề, 2 nút, tỉ lệ, 3 thẻ ngang, 3 nút), thẻ tím tối trên trận, tiêu đề vàng.
Làm đẹp: dải màu độ hiếm trên đỉnh thẻ và chip độ hiếm; hốc icon 72 px; dấu MỚI; dòng chỉ số kẻ mảnh, số không đổi
không tô xanh; thẻ khác tối nhẹ (không mờ). Nút: tấm nổi có gờ, nắp phím vàng, tên + dòng phụ, huy hiệu số lượt (hết
lượt: ổ khoá). Hiệu ứng: tiêu đề rơi vào, thẻ chia lần lượt, thẻ chọn nhô lên, lấy thẻ loé sáng và hai thẻ kia rơi
xuống, Đổi lật thẻ, nút nhô khi trỏ và nén khi bấm.

