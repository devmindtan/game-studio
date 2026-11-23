# Album (bách khoa) — bản thiết kế trên web

Màn mới ở sảnh (bach-ai `production/roadmap.md` mục 5): mọi quái, boss, kỹ năng, vật phẩm. Quái/boss **mở khoá sau
khi hạ lần đầu** (lưu trong slot), chưa mở thì hiện bóng đen "?".

## Tham khảo

| Nguồn | Lấy | Tránh |
|---|---|---|
| Vampire Survivors, Bestiary / Collection ([danh sách bestiary](https://primagames.com/tips/all-bestiary-members-in-vampire-survivors-listed), [wiki Enemies](https://vampire-survivors.fandom.com/wiki/Enemies)) | Hạ quái lần đầu thì mở mục; lưới ô vuông, ô chưa mở là bóng tối | Không có trang chi tiết đủ chỉ số |
| Brotato, Encyclopedia ([Switch 2 Edition](https://www.wikiwand.com/en/articles/Brotato_%E2%80%93_Nintendo_Switch_2_Edition)) | Bách khoa tách theo mục (vũ khí, vật phẩm, quái) | — |

**Quyết định:** 3 mục dạng thẻ (Quái, Boss, Kỹ năng; bỏ Vật phẩm theo người dùng 2026-11-23) đổi bằng Q/E (LB/RB); lưới 7 cột bên trái, khung chi
tiết bên phải; quái ghi loài, hệ yếu (đỏ), hệ kháng (xám), chỉ số ở ải 1, số lần hạ; kỹ năng có ô **mô phỏng** (làm
sau, dùng sân demo của dashboard).

## Bố cục 1280×720

- Trái trên: tiêu đề "Album", dòng tiến độ "Đã mở 7 / 13 quái · 10 kỹ năng". Phải trên: Quay lại (Esc).
- Hàng thẻ mục (150×44) dưới tiêu đề, mục đang mở viền vàng.
- Lưới ô 88×88, cách 8, 7 cột; ô đang chọn viền trắng + vàng; ô chưa mở: bóng đen + "?".
- Khung chi tiết 508×570: ảnh lớn, tên, loài · vùng, yếu/kháng, bảng chỉ số, ghi chú, ô mô phỏng (kỹ năng).

## Ảnh

`shots/album-tab0.png` (Quái, chọn Dơi), `shots/album-tab2.png` (Kỹ năng, chọn Lốc xoáy).

