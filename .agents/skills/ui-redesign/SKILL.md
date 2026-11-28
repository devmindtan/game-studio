---
name: ui-redesign
description: Quy trình thiết kế (lại) giao diện game trên web trước rồi mới vào Godot. Dùng khi người dùng nhờ thiết kế mới hoặc "thiết kế lại" một màn hình, HUD, menu, bảng chỉ số, hay cả bộ giao diện. "Thiết kế lại" nghĩa là một hướng KHÁC hẳn bản cũ, không chỉnh nhẹ bản cũ. English triggers: redesign UI, new UI direction, menu redesign, HUD redesign, web mockup first.
---

# Thiết kế (lại) giao diện: web trước, Godot sau

Người dùng 2026-11-26: "bổ sung quy trình thiết kế giao diện trên web trước, sau đó thiết kế lại giao diện cho game
(khi tôi bảo thiết kế lại là hãy thiết kế theo một cách khác, không làm giống thiết kế cũ)".

## Quy tắc

- **Thiết kế lại = hướng mới.** Không giữ bố cục, khung, bảng màu, kiểu panel của bản cũ rồi chỉnh vài chỗ. Trước khi
  vẽ, ghi ra "Bản cũ" (bố cục, màu, kiểu khung, font, cách điều hướng) để tránh lặp lại; bản mới khác ít nhất ở bố cục
  và ngôn ngữ hình ảnh (khung, màu chủ đạo).
- **Hướng mới không mặc định theo phong cách chung của game** (người dùng 2026-11-28, bach-ai lên cấp: ba hướng đều là
  giấy/gỗ, "cả 3 đều xấu... đừng bám vào cái giấy nữa"): ít nhất 2 trong 3 hướng dùng chất liệu khác phong cách đang
  có; chữ dùng đúng font của game (font của `assets/fonts/` hoặc theme), không dùng font trang trí của lab.
- **Không đoán mò** (AGENTS.md): tham khảo ≥ 2 game cùng thể loại cho màn đó, ghi nguồn + điều học / điều tránh.
- **Web trước.** Không sửa `games/<g>/src` cho tới khi người dùng chọn hướng trên ảnh 1280×720.
- Màn hình game, không phải trang web: 1280×720 cố định, bàn phím/gamepad là chính, chữ ≥ 18 px (xem
  `design-web/README.md`).

## Các bước

1. **Phạm vi**: liệt kê màn trong `games/<g>/production/ui/screens.json` sẽ đổi; chụp bản hiện tại
   (`gamekit ui-shots <g> <màn>`) làm mốc "trước".
2. **Bản cũ**: ghi vào `design-web/games/<g>/specs/<màn>.md` mục "## Bản cũ" (bố cục, màu, khung, font, điều hướng).
3. **Tham khảo**: mục "## Tham khảo" trong cùng file: ≥ 2 game, mỗi game 3 dòng (học gì / tránh gì / quyết định).
   Không có Internet thì ghi rõ đã bỏ bước này.
4. **2–3 hướng** trên web: `design-web/games/<g>/screen-<màn>-<hướng>.html` (+ css/js), khai báo trong `design-web/games/<g>/screens.json` (mỗi hướng một "view"; game mới thì thêm vào `design-web/games.json`), mỗi hướng khác nhau thật sự (ví dụ
   sổ tay da / bàn đá rune / bản đồ giấy), cùng dữ liệu thật của game. `design-web/serve.sh` để xem.
5. **Chụp và soát** mỗi hướng 1280×720 vào `design-web/games/<g>/shots/`, soi từng vùng ×2 (căn chữ, tràn, khoảng cách).
6. **Người dùng xem trên web rồi chọn.** Hướng được chọn ghi `"chosen": true` trong `screens.json`. Chạy `design-web/serve.sh` (nền) và đưa **đường link** từng hướng
   của **Design Lab** (`http://localhost:8770/design-web/#<g>/<màn>/<số hướng>`: cả các hướng nằm trong trang chính, không mở từng trang riêng, người dùng 2026-11-26) ngay trong tin nhắn, kèm ảnh. Không hỏi chọn chỉ
   bằng đường dẫn file (bài học 2026-11-26: người dùng không xem được nên chọn mò, agent port luôn rồi phải hoàn tác).
   Người dùng chưa nói đã xem và chọn thì không port.
7. **Port** hướng đã chọn sang Godot (`UiKit` / theme của game), `gamekit ui-shots <g> <màn>`, so với ảnh web, soi ×2.
   **Đưa thông tin game lên web: giữ cả icon** (người dùng 2026-11-27: "sao bạn dùng toàn chữ không vậy icon của nó
   đâu"): dòng nào trong game có icon (ngôi sao, vàng, đá, tim, kiếm, giày, nội tại…) thì bản web cũng có icon đó,
   lấy từ `design-web/games/<g>/assets/` hoặc sprite của game; trước khi chụp, so từng dòng với ảnh game.
      **Port = chép đúng bản web**, không tự chế (người dùng 2026-11-26: "trên web đã thiết kế hết rồi mà bạn chế cái gì
   vậy"): cùng bố cục trang, cùng tiêu đề/chữ, cùng loại điều khiển (dải đánh dấu là dải đánh dấu, không đổi thành tab;
   màn hai trang là hai trang, không đổi thành hộp nổi). Trước khi code một màn, mở file `screen-*.html` của nó, liệt kê
   từng khối (trang trái / phải / dải / con dấu / gợi ý phím) rồi làm đủ. Chỗ nào game cần mà web không có (nút của
   tính năng cũ, dữ liệu thật dài hơn) thì **thiết kế nó trên web trước** (thêm vào `screen-*.html` / một hướng mới
   trong `screens.json`), gửi link Design Lab, người dùng xem và duyệt rồi mới đưa vào game (người dùng 2026-11-26:
   "Cái nào chưa có trên web thì thiết kế trên web cho tôi xem rồi mới đưa vào game"); không tự thêm vào game. Báo xong phải đặt ảnh game cạnh ảnh
   web của cùng màn và nêu khác biệt còn lại.
8. **Commit**: repo gốc (`design-web/`), repo game (`src/`, `production/ui/`), kèm ảnh trước / sau.

## Pixel sắc nét và không đè chữ (người dùng 2026-11-26)

- Không xoay/nghiêng khung, mẩu giấy, dấu mộc (kể cả `transform: rotate` trên web): pixel bị lấy mẫu lại nên mờ.
  Chỉ chữ dọc xoay đúng 90° với toạ độ nguyên.
- Toạ độ và kích thước khung là số nguyên (mẩu giấy có tâm thì bề rộng chẵn).
- Nội dung trong vùng cuộn chừa lề phải ~18 px cho thanh cuộn; soi ×2 cột phải của mọi bảng cuộn.
- Soát ảnh **nguyên trang** đến cả hai mép sổ (không cắt vùng trước khi nhìn toàn cảnh), và chụp **mọi trạng thái** của
  nút chính (ví dụ Mặc / Bỏ ra, có / không thanh cuộn) — 2026-11-26 con dấu tràn khỏi trang lọt qua vì ảnh bị cắt.
