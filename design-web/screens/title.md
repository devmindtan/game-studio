# Màn chờ + màn tiêu đề (bản thiết kế trên web)

Màn đầu tiên người chơi thấy. Bản thiết kế này giữ nguyên nhận diện của game (logo **BÁCH ẢI**,
đồng cỏ tối, hai nhân vật trên bệ, một cột nút) nhưng sửa lại nhịp đọc và cảm giác game:

- Tách **màn chờ** (nhấn phím) khỏi **menu chính**, như các game survivor-like.
- Menu có **một hành động chính** rõ (Tiếp tục), các nút còn lại lùi về sau.
- Bỏ chữ 14 px; mọi chữ trong khung ≥ 18 px.
- Panel/button vuông, viền dày, bevel, góc trang trí; không dùng card bo tròn kiểu web.
- Thêm chiều sâu: trăng, núi xa, sương trôi, bệ đá có vòng rune xoay, nhân vật idle.

## Trạng thái

| Trạng thái | Hiển thị | Vào / ra |
|---|---|---|
| `gate` (màn chờ) | Logo, tagline, hai nhân vật, dòng **NHẤN PHÍM BẤT KỲ** nhấp nháy | Mở game; phím bất kỳ hoặc bấm chuột → `menu` |
| `menu` | Logo, tagline, hai nhân vật, cột 4 nút; nút đầu focus sẵn | `Esc` → `gate` |

## Bố cục (1280×720)

### Biến thể A · Cổ điển (mặc định)

```text
┌──────────────────────────────────────────────────────────────┐
│  ┌ góc                      BÁCH ẢI                      góc ┐ │
│  │                       ◆ Vượt trăm ải ◆                   │ │
│  │                                                          │ │
│  │   [Kiếm sĩ]          ┌────────────────────┐   [Pháp sư]  │ │
│  │      🧍              │  Tiếp tục (86 px)  │       🧍     │ │
│  │    bệ đá             ├────────────────────┤     bệ đá    │ │
│  │                      │  Chọn nhân vật 56  │              │ │
│  │                      │  Cài đặt       56  │              │ │
│  │                      │  Thoát         56  │              │ │
│  │                      └────────────────────┘              │ │
│  │  Phiên bản 0.6.21              ↑↓ chọn · Enter xác nhận  │ │
│  └ góc                                                  góc ┘ │
└──────────────────────────────────────────────────────────────┘
```

- Logo: tâm ngang, `top: 68`, cỡ 112 px, gradient vàng → vàng sẫm, bóng cứng 4 px.
- Đường kẻ + kim cương dưới logo, rộng 420 px; tagline 23 px, giãn chữ 7 px.
- Cột nút: rộng 432 px, tâm ngang, `top: 296`, cách nhau 12 px.
- Nút chính cao 86 px (tiêu đề 34 px + dòng phụ 18 px); nút thường cao 56 px, chữ 27 px.
- Nhân vật: khung 48×48 scale ×6 = 288 px, cách mép 64 px; bệ đá tâm tại `y = 264` trong khung
  (điểm chân của sprite), vòng rune 252×62 xoay chậm.
- Đáy: phiên bản trái, phím tắt phải, cách mép 78 px, chữ 18 px.
- Vùng an toàn kiểm tra là **64 px mỗi cạnh** (5% chiều ngang): logo, menu, nhân vật, bệ đá đều nằm trong.
  Riêng dòng phiên bản/phím tắt cố ý ở ngoài (thông tin phụ, không phải UI tương tác).

### Biến thể B · Điện ảnh

- Logo + menu dồn trái (`left: 76`), logo `top: 64`, cỡ 88 px, menu `top: 280`.
- Hai nhân vật đứng cạnh nhau bên phải (`right: 322` và `right: 64`), thấp hơn 32 px.
- Vòng tròn rune lớn (520 px, mờ 14%) làm nền phía sau hai nhân vật.
- Màn chờ cũng dồn trái; phù hợp nếu sau này muốn đặt key art lớn bên phải.

## Màu

| Vai trò | Mã | Ghi chú |
|---|---|---|
| Nền ink | `#070b10` | nền ngoài, viền nút |
| Nền cỏ | `#0c1713` → `#070f0c` | tối dần xuống đáy |
| Vàng | `#e8c574` | logo, viền focus, kim cương |
| Vàng sẫm | `#a8874a` | viền nút, gradient logo |
| Chữ kem | `#f2e6c9` | chữ nút |
| Chữ mờ | `#b9b29c` | phụ đề, phím tắt |
| Đỏ chính | `#c04a3e` → `#7e2b2b` | nút Tiếp tục |
| Đỏ kiếm sĩ | `#d94a4a` | rune bệ trái |
| Tím pháp sư | `#8b5cf6` | rune bệ phải |

Tương phản chữ/nền đều vượt 4.5:1 ở các cặp chính; trạng thái focus không chỉ đổi màu mà còn có
viền ngoài, caret và độ sáng.

## Chữ

- **VT323** (OFL), phủ đủ tiếng Việt: `ế ụ ậ Ả ư ợ đ`.
- Cỡ trong khung 1280×720: logo 112/88, tiêu đề nút 34/27, phụ 18, phím tắt 18, tagline 23.
- Không dùng chữ dưới 18 px; không dùng font hệ điều hành trong khung game.

## Chuyển động

| Thành phần | Nhịp |
|---|---|
| Nhân vật idle | 4 frame, 0,76 s, `steps(4)` |
| Vòng rune | xoay 0,35 rad/s, nhấp nháy theo pha từng điểm |
| Sương | trôi ngang 46 s |
| Logo | thở nhẹ 5,5 s (chỉ đổi glow) |
| Màn chờ | nhấp nháy 1,5 s `steps(2)` |
| Vào menu | trượt lên 16 px, 0,28 s `steps(4)` |
| Focus | caret nhấp nháy 0,9 s |

`prefers-reduced-motion` tắt toàn bộ animation.

## Phím và tiếp cận

- `↑` `↓` / `W` `S`: đổi nút; `Enter` / `Space`: xác nhận; `Esc`: về màn chờ.
- `Tab` / `Shift+Tab` cũng đổi nút (không nhảy ra khỏi khung game).
- Chuột: hover đổi focus, click xác nhận — nhưng mọi thứ làm được chỉ bằng bàn phím.
- Nút là `<button>` thật, có `aria-label`; focus hiển thị bằng viền vàng + caret, không chỉ đổi màu.
- Toast xác nhận hành động (bản thử chưa nối scene).

## Đưa vào Godot

- `src/front/title.gd`: thêm trạng thái `gate` trước menu; đổi `MENU_W` 440 → 432, nút chính 84 → 86,
  nút thường 54 → 56, chữ 21 → 27, phím tắt 14 → 18.
- `UiKit`: panel/button thêm viền ngoài 2 px đen, bevel trên/dưới, góc vàng; focus thêm caret trái.
- Font: cân nhắc nhúng VT323 (OFL) cho toàn bộ front-end; nếu giữ DejaVuSans thì vẫn phải tăng cỡ chữ.
- Kiểm: `gamekit ui-shots bach-ai 00-title 00a-title-new` rồi soi từng vùng ×2.

## Tham khảo

| Nguồn | Học gì | Tránh gì | Quyết định |
|---|---|---|---|
| [Vampire Survivors Wiki · Main menu](https://vampire.survivors.wiki/w/Main_menu) | Màn hình đầu là **"PRESS TO START"** nhấp nháy rồi mới vào menu; menu có một nút **Start** nổi nhất, các mục phụ (Options/Quit) tách lên thanh trên. | Menu quá nhiều mục khi mới chơi; nút phụ chen ngang hàng với nút chính. | Tách `gate` → `menu`; giữ 4 mục, Tiếp tục là nút chính duy nhất. |
| [Wandr · Game Menu Design](https://www.wandr.studio/blog/game-menu-design) | Menu chính phải đưa người chơi vào game nhanh, độ sâu menu nông, điều hướng controller/touch được thiết kế từ đầu. | Menu nhiều tầng, thao tác chỉ làm được bằng chuột. | Một cột nút, `Enter`/`Esc` đủ dùng, không mở submenu trong bản thử. |
| [StraySpark · Game UI/UX Principles](https://www.strayspark.studio/blog/game-ui-ux-design-principles) | Test **chỉ bằng controller**: mọi phần tử phải tới được, mọi hành động phải có phản hồi. | Phản hồi quá nhiều hoặc không có phản hồi. | Focus caret + viền vàng + toast ngắn; không thêm hiệu ứng thừa. |
| [`games/bach-ai/design/ux/front-end.md`](../../games/bach-ai/design/ux/front-end.md) | Luồng tiêu đề → chọn nhân vật → sảnh; nút Tiếp tục đặt trên Chơi mới; icon vector cho nút sảnh. | Đoán bố cục không dựa vào game cùng loại. | Giữ nguyên luồng và thứ tự nút hiện có. |

Ghi chú: API tìm kiếm web của agent trả HTTP 402, nên bước tìm tự động bị bỏ qua; các nguồn trên lấy
bằng `webfetch` trực tiếp (DuckDuckGo HTML + wiki). Ảnh tham khảo chỉ để đọc bố cục, không dùng làm asset.
