# Cấu trúc vũ khí (Sprite Lab)

Vũ khí được chia theo **loại (type)** và **chất liệu/cấp (tier/material)** để dễ mở rộng biến thể.

## Loại vũ khí

| Loại | Mô tả | Kích thước gợi ý | Hiệu ứng đánh thường (tham chiếu) |
|---|---|---:|---|
| `sword` (nhỏ) | Kiếm một tay, tầm ngắn-vừa | 24x24 | `sword-slash` |
| `greatsword` (sword lớn) | Đại kiếm hai tay, tầm rộng | 32x32 | `sword-slash` (mở rộng) |
| `dagger` | Dao găm, rất nhanh/tầm ngắn | 20x20 | `dagger-slash` |
| `axe` | Rìu, chém nặng | 32x32 | — |
| `hammer` | Búa, đập gây choáng | 32x32 | — |
| `bow` | Cung, tấn công tầm xa | 24x32 | projectile `arrow` |
| `magic-staff` | Gậy phép, dẫn phép thuật (đỉnh gắn ngọc) | 24x32 | `staff-strike`, projectile `arcane-bolt` |
| `staff` | Gậy võ thuật (bo staff/quyền trượng, cán thẳng cân đối, quấn tay) | 24x32 | `staff-strike` |
| `shield` | Khiên, phòng thủ/đỡ đòn | 32x32 | — |

## Quy ước đặt tên biến thể

`<loại>-<chất_liệu>` (hoặc `<loại>-<tier>`), ví dụ: `axe-wood`, `axe-iron`, `axe-gold`.

Chất liệu cơ bản: `wood` (gỗ), `iron` (sắt), `gold` (vàng). Có thể mở rộng: `steel`, `silver`, `obsidian`, `mythic`, …

## Biến thể hiện có (taxonomy)

| Loại | wood | iron | gold |
|---|---|---|---|
| sword (nhỏ) | `sword-wood` | `sword-iron` | `sword-gold` |
| greatsword (lớn) | `greatsword-wood` | `greatsword-iron` | `greatsword-gold` |
| dagger | `dagger-wood` | `dagger-iron` | `dagger-gold` |
| axe | `axe-wood` | `axe-iron` | `axe-gold` |
| hammer | `hammer-wood` | `hammer-iron` | `hammer-gold` |
| bow | `bow-wood` | `bow-iron` | `bow-gold` |
| magic-staff | `magic-staff-wood` | `magic-staff-iron` | `magic-staff-gold` |
| staff | `staff-wood` | `staff-iron` | `staff-gold` |
| shield | `shield-wood` | `shield-iron` | `shield-gold` |

## Sprite vũ khí legacy (giữ tương thích)

`iron-sword`, `greatsword`, `battle-axe`, `war-hammer`, `magic-staff`, `oak-bow`, `round-shield`, `tower-shield` — giữ nguyên để không phá tham chiếu hiện có; ưu tiên dùng tên taxonomy cho vũ khí mới.

## Ghi chú thiết kế

- Vũ khí là vật phẩm (item) tĩnh: animation `idle`, neo gần tay cầm/điểm tựa, có hitbox bbox (rect) đo từ pixel.
- Khi tạo biến thể mới: giữ form/silhouette theo loại, đổi palette/chất liệu và chi tiết; render `gamekit art run <tên>` rồi kiểm tra `preview.png`/hitbox.
- Hiệu ứng tấn công là sprite riêng (có hitbox chiến đấu), không vẽ vào sprite vũ khí.
