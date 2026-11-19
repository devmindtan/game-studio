# Tiêu chuẩn sinh vật `creature-v1` (quái, thú, boss)

Người dùng 2026-11-19: sinh vật trông "đơ như tượng, chỉ có chân di chuyển"; cần quy trình rõ (độ phân giải,
số khung, mô tả từng động tác) và mọi động tác phải sống động. Tiêu chuẩn này là điều kiện xong;
`sheet.export` (chạy trong `gamekit art run`) **từ chối** sprite có `brief.json` mà không đạt.

## Tham khảo

| Nguồn | Điều lấy |
|---|---|
| [SLYNYRD Pixelblog 25: motion cycles](https://www.slynyrd.com/blog/2020/1/23/pixelblog-25-motion-cycles), [Pixelblog 8](https://slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation) | Chu kỳ chạy 6 khung là chuẩn; bỏ khung thì giảm tốc phát; tư thế sải phải mạnh, thân nghiêng tới. |
| [Adobe: run cycle](https://www.adobe.com/uk/creativecloud/animation/discover/animation-run-cycle.html) | Chạy ≥ 8 khung; khung chạm đất là pose chính; có lúc mọi chân rời đất. |
| [Zivatar: 2D wolf animation](https://zivatar.itch.io/2d-wolf-animation-asset), [OpenGameArt: pixel wolf](https://opengameart.org/content/pixel-wolf) | Sói: đi 11, chạy 8, idle 9 khung; nhảy 4. |
| [Sprite-AI: how many frames](https://www.sprite-ai.art/blog/sprite-animation-frames), [dev.to: frames a sprite needs](https://dev.to/nitin_808a59e08de0d0385ab/how-many-frames-does-a-sprite-animation-need-24k9) | idle 2–6, đi 6–8, đánh 4–8, trúng đòn 2–3, chết 4–10 (boss ≥ 10). **Gồng là thiết kế gameplay** (cho người chơi né); đòn phải kết thúc về được dáng nghỉ. |
| Gói quái thương mại ([Cyangmou side-scroller enemies](https://cyangmou.itch.io/pixel-side-scroller-enemies-1), Metroidvania monsters) | Quái đẹp dùng: idle 5–6, đi 6–9, đánh 6–14, trúng đòn 3–7, chết 6–15. |

## Độ phân giải (1 pixel = 1 đơn vị, không phóng/thu)

| Cỡ | Khung | Ví dụ |
|---|---|---|
| nhỏ | 24–32 px | dơi, ma trơi, cóc |
| vừa | 32–48 px | sói, yêu tinh, nấm, bọ |
| boss | 48–72 px | Vua Thạch Nhầy, Mộc Yêu, Cóc Chúa |

Sinh vật ≤ 32 px vẽ tay (ASCII) từng tư thế; lớn hơn có thể dựng từ bộ phận (thư viện như `lib/toadkit.py`)
nhưng **mỗi khung là một tư thế riêng**, không phải cùng một hình dời chỗ.

## Động tác bắt buộc và số khung tối thiểu

| Động tác | Khung tối thiểu | Phải có |
|---|---|---|
| `move` (lặp; game dùng làm cả lúc đứng) | 6 | thân nhấp nhô theo bước, đầu gật, đuôi/tai/cánh/áo chuyển động trễ một nhịp (**overlapping action**), không chỉ chân |
| `attack` | 6 | **gồng ≥ 2 khung** đổi dáng rõ (dựng lông, nhe nanh, mắt lóe, thu người) → ra đòn ≥ 1 → **thu về ≥ 2** |
| `hurt` | 3 | khựng (chớp sáng) → giật lùi, đầu ngửa → hồi lại |
| `death` | 6 | ngã/vỡ có trọng lượng (nảy nhẹ khi chạm đất), rồi tan/mờ dần |
| quái nhảy: `crouch` + `jump` | 2 + 4 | nén → bật → đỉnh → rơi → đáp (luật 2026-11-18) |

**Boss** (`"size": "boss"` trong brief, người dùng 2026-11-19): `move` 8, `attack` 8, `hurt` 4, `death` 8; boss nhảy
thêm `crouch` 4 + `jump` 8.

## Kiểm tra tự động (`brief.json` cạnh `gen.py`)

```json
{"standard": "creature-v1", "size": "medium",
 "frames": {"move": ["…mô tả khung 1…", "…"], "attack": ["…"], "hurt": ["…"], "death": ["…"]}}
```

- Mỗi động tác bắt buộc có trong sprite, đủ số khung tối thiểu, và **số dòng mô tả = số khung** (vẽ khung nào
  phải nói khung đó làm gì).
- **Sống động:** trong `move`, mỗi cặp khung liền nhau phải đổi ≥ 4 % số điểm ảnh ở **60 % phía trên** của hình
  (thân, đầu, đuôi), không chỉ ở chân. Khung gồng đầu tiên của `attack` phải khác khung đầu của `move` ≥ 8 % ở
  phần trên (đổi dáng thật).
- Game: test `monster_standard_test.gd` của Bách Ải yêu cầu mọi quái có `brief.json` chuẩn này (danh sách
  quái cũ đang chờ nâng cấp ghi trong test, chỉ được thu hẹp).
