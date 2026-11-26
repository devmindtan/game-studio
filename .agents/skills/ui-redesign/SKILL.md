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
- **Không đoán mò** (AGENTS.md): tham khảo ≥ 2 game cùng thể loại cho màn đó, ghi nguồn + điều học / điều tránh.
- **Web trước.** Không sửa `games/<g>/src` cho tới khi người dùng chọn hướng trên ảnh 1280×720.
- Màn hình game, không phải trang web: 1280×720 cố định, bàn phím/gamepad là chính, chữ ≥ 18 px (xem
  `design-web/README.md`).

## Các bước

1. **Phạm vi**: liệt kê màn trong `games/<g>/production/ui/screens.json` sẽ đổi; chụp bản hiện tại
   (`gamekit ui-shots <g> <màn>`) làm mốc "trước".
2. **Bản cũ**: ghi vào `design-web/screens/<màn>.md` mục "## Bản cũ" (bố cục, màu, khung, font, điều hướng).
3. **Tham khảo**: mục "## Tham khảo" trong cùng file: ≥ 2 game, mỗi game 3 dòng (học gì / tránh gì / quyết định).
   Không có Internet thì ghi rõ đã bỏ bước này.
4. **2–3 hướng** trên web: `design-web/screen-<màn>-<hướng>.html` (+ css/js), mỗi hướng khác nhau thật sự (ví dụ
   sổ tay da / bàn đá rune / bản đồ giấy), cùng dữ liệu thật của game. `design-web/serve.sh` để xem.
5. **Chụp và soát** mỗi hướng 1280×720 vào `design-web/shots/`, soi từng vùng ×2 (căn chữ, tràn, khoảng cách).
6. **Người dùng chọn** (hỏi kèm ảnh). Chưa chọn thì không port.
7. **Port** hướng đã chọn sang Godot (`UiKit` / theme của game), `gamekit ui-shots <g> <màn>`, so với ảnh web, soi ×2.
8. **Commit**: repo gốc (`design-web/`), repo game (`src/`, `production/ui/`), kèm ảnh trước / sau.
