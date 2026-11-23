# Kế hoạch: nhân vật ghép từ phần tĩnh, chuyển động bằng code (cutout)

Người dùng 2026-11-23: "tách ra đầu, thân, tay, chân hoàn toàn tĩnh, sau đó xử lí chuyển động bằng code thay vì vẽ".
Trạng thái: **kế hoạch, chưa làm**. Việc Cung thủ (design/archer.md của bach-ai) tạm dừng tới khi xong bước 3 dưới đây.

## Vì sao

Hiện mỗi khung (idle 4, run 8, hurt 3, dash 5, death 5) được vẽ lại toàn bộ bằng `minifig.py`. Đổi cách cầm vũ khí
(cung: sau lưng → ngang → dựng đứng) phải vẽ lại cả 25 khung và dễ sai. Với phần tĩnh + chuyển động bằng code:
vẽ mỗi phần một lần; đổi vũ khí, trang bị, tư thế chỉ là đổi một ảnh hoặc một con số; animation mới không cần vẽ thêm.

## Cách làm (đề xuất)

- **Phần tĩnh** (Sprite Lab): mỗi nhân vật xuất các ảnh rời, mỗi ảnh có **điểm khớp** (pivot) trong json:
  `head`, `torso`, `arm_back`, `arm_front` (cánh tay + bàn tay), `leg_back`, `leg_front`, `weapon` (+ `hair`/`cape` nếu có).
  Cỡ vẫn minifig 48×48 (thân ~26 px), cùng palette và viền 1 px như hiện nay.
- **Khung xương nhỏ** (addon gamekit, dùng chung mọi game): `PartsRig` = cây Node2D (hông → thân → đầu / vai → tay →
  vũ khí; hông → chân), mỗi khớp một góc + độ dời. Vẽ bằng `draw_texture` với góc làm tròn theo bước (giữ pixel sắc, không xoay mịn
  từng độ), hoặc xoay theo bước 45°/22,5° với ảnh vẽ sẵn cho tay/vũ khí nếu xoay làm vỡ nét (thử ở bước 2).
- **Chuyển động bằng code**: `idle` (thở: thân nhấp 1 px), `run` (chân/tay đánh sin ngược pha, nhún theo bước),
  `hurt`, `dash`, `death` (ngã theo góc) viết thành hàm theo thời gian, tham số trong json (biên độ, tần số), không vẽ khung.
- **Vũ khí gắn vào tay** theo điểm khớp: đổi cách cầm = đổi góc/độ dời trong json (cung dựng đứng tay buông, cầm ngang…).
- **Trang bị** thay ảnh của đúng phần (mũ → `head`, giáp → `torso`…), thay cho hệ lớp hiện tại.

## Tham khảo cần tra trước khi làm (quy tắc "không đoán mò")

- Godot 4.7: `Skeleton2D` / `Bone2D` và hướng dẫn "Cutout animation" trong `docs/engine-reference/godot/`; so với tự viết
  cây Node2D (nhẹ, dễ test headless).
- Cách các game pixel làm cutout mà vẫn sắc nét (xoay theo bước, ảnh tay theo góc).

## Các bước (mỗi bước một commit, có test + ảnh)

1. Tra cứu ở trên, ghi kết luận vào file này (chọn Skeleton2D hay cây Node2D, xoay mịn hay theo bước).
2. Sprite Lab: tách phần tĩnh cho **một** nhân vật thử (đề xuất: ranger) + json điểm khớp; `gamekit art run` xuất các phần.
3. Addon `PartsRig` + idle/run bằng code; trang thử trong lab (`art shot … move`), so với sprite cũ; người dùng duyệt.
4. hurt / dash / death bằng code; test headless (vị trí khớp theo thời gian, chân chạm đất).
5. Đưa vào bach-ai cho ranger (Run vẽ qua `PartsRig` thay vì `SpriteSheet`), `gamekit test` + `shot`.
6. Chuyển swordsman và mage (sau khi người dùng duyệt bước 5), rồi trang bị.
7. Quay lại Cung thủ (design/archer.md bước 4–5).

## Câu hỏi cho người dùng (trước bước 2)

- Chỉ nhân vật chính, hay cả quái dạng người?
- Giữ nét pixel tuyệt đối (xoay theo bước, có thể cần vẽ vài góc cho tay/vũ khí) hay chấp nhận xoay mịn?
