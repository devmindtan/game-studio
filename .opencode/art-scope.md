# OpenCode: chỉ làm vật thể và hiệu ứng, không làm nhân vật

Chỉ OpenCode đọc file này (khai báo ở `opencode.json` → `instructions`). Áp dụng cho mọi việc art pixel
trong workspace: `sprite-lab/` và `games/<g>/assets/sprites/`.

## Được làm

- **Vật phẩm**: item, vũ khí như một vật (kiếm, khiên, gậy rơi trên đất), tiền, rương, chìa khoá, bẫy,
  bệ đá, đạo cụ.
- **Hiệu ứng**: viên đạn/projectile, tia phép, vụ nổ/impact, mảnh vỡ, hạt, khói, lửa, sét, hào quang,
  vệt chém, sóng xung kích.
- **Khác**: icon UI, tile, prop/trang trí môi trường, sprite hiệu ứng gắn với chiêu thức.

## Không làm

- **Nhân vật**: người, quái dạng người, boss, NPC — kể cả animation `idle/run/jump/attack/spell/hurt/death`
  của nhân vật.
- Không sửa `gen.py`, PNG, JSON của sprite nhân vật đã có (ví dụ `sprite-lab/sprites/mage/`).
- Không dùng pose rig (`gamekit art rig …`) để dựng nhân vật, không `gamekit art promote` nhân vật vào game.
- Không tự phối đồ LPC để tạo nhân vật. Nhận ZIP LPC do người dùng đưa thì vẫn chạy `gamekit sprites` bình thường.

## Khi được nhờ làm nhân vật

Nói ngay là nhân vật nằm ngoài phạm vi của OpenCode trong workspace này, rồi đề nghị chuyển việc đó sang
công cụ/agent chuyên nhân vật hoặc để người dùng tự vẽ. Không làm thay, không "thử một chút cho biết".

## Hiệu ứng cho nhân vật thì vẫn được

Ví dụ "chiêu của pháp sư bắn ra tia": chỉ làm projectile và impact (như `sprite-lab/sprites/arcane-bolt/`),
không đụng vào sprite pháp sư. Nếu hiệu ứng cần bám theo một pose nhân vật, mô tả bằng thông số
(điểm xuất phát, hướng bay, tốc độ) để game tự gắn, không vẽ lại nhân vật.
