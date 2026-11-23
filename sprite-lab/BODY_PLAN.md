# Kế hoạch: hệ cơ thể nhân vật kiểu LPC, chibi, khung 64×64

Người dùng 2026-11-23: "giữ phong cách chibi dễ thương nhưng làm theo kiểu 64x64 của LPC; di chuyển và các chuyển động học
theo LPC, không lấy (không hẳn là open source)". Thay kế hoạch cutout (tách phần + xoay bằng code) đã bỏ cùng ngày.
Trạng thái: **kế hoạch**. Cung thủ (bach-ai design/archer.md) tạm dừng tới khi bước 6 xong.

## Học gì từ LPC (chỉ cách tổ chức + nhịp chuyển động; KHÔNG chép ảnh, KHÔNG dùng file của tools/lpc-generator)

- **Khung chuẩn 64×64**, một cơ thể gốc cố định: mọi lớp (thân, đầu, tóc, áo, quần, giày, găng, vũ khí) là một tấm sprite
  riêng, cùng bố cục khung, chồng lên nhau là khớp. Đồ mới = vẽ một tấm, mọi nhân vật dùng được.
- **Thứ tự lớp** theo bảng (như `scripts/zPositioning/z_positions.csv` của LPC): áo choàng sau < chân < thân < áo < đầu
  < tóc < mũ < vũ khí; vài lớp đổi thứ tự theo hướng/animation (cung ra trước khi bắn).
- **Animation và số khung** (`sources/state/constants.ts` ANIMATION_CONFIGS): walk 9 (chu kỳ 8), spellcast 7, thrust 8,
  slash 6, shoot 13, hurt 6, idle 2–3, run, jump, combat idle. Mình dùng cùng tên và nhịp khung đó để có cử động "đủ".
- **Cầm vũ khí theo animation**: cung chỉ giương lên ở `shoot`; khi đi cung buông bên tay (rule pixel-sprite 0b).

## Của riêng mình

- **Chibi dễ thương**: đầu to (~45% chiều cao), thân ngắn, tay chân ngắn, mắt to; nhân vật cao ~36–40 px trong khung 64
  (chừa chỗ cho vũ khí/oversize), neo giữa hai bàn chân như hiện nay.
- **Hướng**: game nhìn ngang trái/phải (lật ảnh) → mỗi animation chỉ vẽ **hướng phải** (LPC vẽ 4 hướng). Hỏi người dùng nếu
  muốn thêm hướng lên/xuống.
- Vẽ bằng code Python trong Sprite Lab (palette, viền 1 px, không dither), nhưng **mỗi tấm vẽ trên khung xương chuẩn**:
  `lib/chibi_body.py` giữ vị trí các khớp (đầu, vai, tay, hông, chân) cho từng khung của từng animation; mỗi lớp đồ chỉ
  vẽ theo các khớp đó → đổi đồ không đụng tới chuyển động.

## Các bước (mỗi bước một commit, có ảnh + test)

1. `lib/chibi_body.py`: bảng khớp chuẩn 64×64 cho idle, walk (học nhịp LPC) + tấm thân trần; xem ảnh, người dùng duyệt
   dáng chibi (2–3 phương án tỉ lệ đầu/thân theo rule nhân vật mới).
2. Thêm hurt, death, dash, shoot, slash, spellcast trên cùng bảng khớp.
3. Ghép lớp: định dạng xuất (mỗi lớp một strip + json thứ tự lớp), `gamekit art` hiểu nhân vật nhiều lớp; test khớp khung.
4. Addon gamekit: vẽ nhân vật nhiều lớp trong game (thay `SpriteSheet` đơn), trang bị = đổi tấm của lớp.
5. Bộ đồ đầu tiên: Cung thủ (tóc đuôi ngựa, áo chẽn, cung) → đưa vào bach-ai, `gamekit test` + `shot`.
6. Chuyển Kiếm sĩ, Pháp sư; rồi trang bị. Sau đó quay lại Cung thủ bước 4 (các chiêu).

## Ảnh hưởng tới quy tắc hiện tại

- Quy tắc "nhân vật minifig 48×48 (thân ~26 px)" (AGENTS.md, 2026-11-22) đổi thành khung 64×64 chibi kiểu LPC cho
  nhân vật dạng người mới; nhân vật cũ giữ 48×48 tới khi chuyển ở bước 6.
