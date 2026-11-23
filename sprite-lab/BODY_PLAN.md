# Nhân vật: dùng LPC adult (chốt 2026-11-23)

Người dùng 2026-11-23: thử tự vẽ chibi 64×64 bằng code → "xấu quá"; quyết định "sử dụng của LPC luôn", thân **adult**.
(Thân child gần chibi nhưng không có vũ khí, bắn cung, phép; teen bị bỏ qua.) Bản chibi tự vẽ (`lib/chibi_body.py`,
`sprites/chibi-base`, `designs/chibi-body`) chỉ còn là thử nghiệm.

## Bộ đồ 3 class (URL của trình tạo, `gamekit lpc` → http://localhost:5173/)

- Kiếm sĩ: `#?body=Body_color_light&head=Human_Male_light&hair=Natural_chestnut&armour=Plate_steel&legs=Long_Pants_gray&shoes=Basic_Boots_brown&weapon=Arming_Sword_steel&shield=Round_Shield_silver`
- Pháp sư: `#?body=Body_color_light&head=Human_Male_light&hair=Natural_white&clothes=Longsleeve_purple&legs=Long_Pants_purple&belt=Robe_Belt_white&hat=Wizard_Hat_Base_base_red&weapon=Simple_staff_simple&shoes=Basic_Boots_brown`
  (áo choàng Robe chỉ có bản nữ)
- Cung thủ: `#?body=Body_color_light&head=Human_Male_light&hair=Ponytail_redhead&vest=Vest_forest&legs=Pants_brown&shoes=Basic_Boots_brown&weapon=Recurve_medium&ammo=Ammo_arrow&quiver=Quiver_quiver`

Xuất tự động (không cần bấm tay): Playwright trong `tools/lpc-generator/node_modules` mở URL, bấm "ZIP: Split by
animation", lưu vào `games/bach-ai/assets/source/lpc/<class>.zip`; rồi `gamekit sprites bach-ai`.

## Các bước còn lại (mỗi bước một commit, test + ảnh)

1. ✅ 3 ZIP + `gamekit sprites` (17 animation mỗi nhân vật, credit ghi vào `assets/credits/`).
2. Trận: vẽ anh hùng bằng `LpcCharacter` (hướng trái/phải hoặc 4 hướng), hitbox/thân theo khung 64, các hiệu ứng gắn người.
3. Chiêu cầm vũ khí: Cung thủ dùng `shoot`, Pháp sư `spellcast`, Kiếm sĩ `slash` (kiếm Arming Sword thiếu slash 64 px: chọn kiếm khác có slash).
4. Sảnh, tạo nhân vật, Album, trang bị (trang bị = đổi lớp LPC), màn Credits đọc `assets/credits/`.
5. Bỏ sprite minifig cũ khỏi game; quay lại Cung thủ (design/archer.md bước 4).
