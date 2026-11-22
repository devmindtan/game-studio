# Màn chờ + màn tiêu đề (bản thiết kế trên web)

Màn đầu tiên người chơi thấy. Đây là **thiết kế lại**, không phải bản làm đẹp của bố cục cũ
(logo trên, hai tướng hai bên, một cột nút giữa): ba phương án dưới đây có **bố cục khác nhau**,
không phải ba lần đổi màu cùng một layout.

Điểm chung (giữ nhận diện game): logo **BÁCH ẢI**, đồng cỏ đêm, hai nhân vật Kiếm sĩ / Pháp sư
(sprite có sẵn của game), bệ đá có vòng rune, chữ tiếng Việt, font pixel, khung 1280×720.

## Trạng thái

| Trạng thái | Hiển thị | Vào / ra |
|---|---|---|
| `gate` (màn chờ) | Logo, hai tướng, dòng **NHẤN PHÍM BẤT KỲ** nhấp nháy; menu ẩn | Mở game; phím bất kỳ hoặc bấm chuột → `menu` |
| `menu` | Logo, hai tướng, menu 4 mục; mục đầu focus sẵn | `Esc` → `gate` |

## Ba phương án bố cục

### A · Cổng ải — menu nằm trong cổng đá

Cổng đá cao 560 px ở giữa màn hình; logo khắc trên mặt cổng, menu là các bia đá trong vòm cổng,
hai tướng đứng nhỏ hai bên chân cổng. Cổng là khung của toàn màn, không phải nền trang trí.

```text
┌──────────────────────────────────────────────────────────────┐
│                                          ☾                   │
│                ┌────────────────────────┐                    │
│                │        BÁCH ẢI         │  ← mặt cổng (đá)   │
│                │      Vượt trăm ải      │                    │
│  🧍            │  ╭──────────────────╮  │            🧍      │
│  bệ đá         │  │  Tiếp tục (88)   │  │          bệ đá     │
│                │  │  Chọn nhân vật   │  │                    │
│                │  │  Cài đặt         │  │                    │
│                │  │  Thoát           │  │                    │
│                │  ╰── bậc đá ────────╯  │                    │
│                └────────────────────────┘                    │
│  Phiên bản 0.6.21              ↑↓ chọn · Enter · Esc         │
└──────────────────────────────────────────────────────────────┘
```

- Cổng: 540×560, tâm ngang, `top: 96`; mặt đá có đường xếp khối, hai cột sáng viền, hai bó đuốc
  ở hai bên (lửa nhấp nháy), bậc đá 3 tầng ở đáy vòm.
- Lintel cao 120 px: logo 62 px + đường kẻ + tagline 18 px (chữ khắc, không phải logo nổi).
- Vòm trong: cách mép 32 px, bán kính 238 px; menu rộng 360 px, `top: 262`.
- Nút: chính 88 px (tiêu đề 32, phụ 18), còn lại 54 px (chữ 26).
- Tướng: scale ×4 (192 px), khung 300×276, `bottom: 62`; bệ 240 px; cách mép 40 px.
- Màn chờ: dòng nhấn phím ở `top: 430`, có hoa văn kim cương phía trên.

### B · Dải băng — logo góc trái, menu ngang ở đáy

Logo thành măng-sét góc trái; hai tướng đứng cạnh nhau giữa màn; menu là một dải băng ngang
sát đáy, mục chính cao hơn và rộng hơn. Thông tin phụ (phiên bản, phím) dồn lên góc phải trên.

```text
┌──────────────────────────────────────────────────────────────┐
│  BÁCH ẢI                            Phiên bản · ↑↓ Enter Esc  │
│  ◆ Vượt trăm ải                                              │
│                                                              │
│                     🧍        🧍                             │
│                   bệ đá     bệ đá      ◯ vòng rune mờ        │
│                                                              │
│  ┌──────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Tiếp tục    │ │Chọn nhân vật│ │ Cài đặt  │ │  Thoát   │  │
│  │  · ải 10     │ │            │ │          │ │          │  │
│  └──────────────┘ └────────────┘ └──────────┘ └──────────┘  │
└──────────────────────────────────────────────────────────────┘
```

- Logo 96 px tại `78/64`; tagline 22 px; vòng tròn rune lớn (440 px, mờ 14%) sau hai tướng.
- Tướng: scale ×5 (240 px), khung 340, `bottom: 170`, tâm x 700 và 990; bệ 260 px.
- Menu: dải ngang rộng 1044, `bottom: 64`, các mục cao bằng đáy; chính 300×96, còn lại 236×64.
- Màn chờ: dòng nhấn phím ở góc trái dưới (`78/512`) đúng chỗ menu sẽ hiện.
- Không có trăng: vòng rune đã là hình tròn lớn bên phải, thêm trăng sẽ chồng.

### C · Cuộn giấy — menu viết trên cuộn giấy da

Một cuộn giấy da mở dọc bên trái, menu viết bằng mực; hai tướng đứng trên con đường đá bên phải;
logo nhỏ ở góc trái trên. Đây là hướng "diegetic": menu là vật thể trong thế giới game.

```text
┌──────────────────────────────────────────────────────────────┐
│  BÁCH ẢI                                    ☾                │
│  ◆ Vượt trăm ải                                              │
│  ╔════════════════════╗                                      │
│  ║   (con dấu cổng)   ║        🧍        🧍                   │
│  ║  ▸ Tiếp tục        ║      bệ đá     bệ đá                 │
│  ║  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈  ║        đường đá dẫn vào ải          │
│  ║    Chọn nhân vật   ║                                      │
│  ║    Cài đặt         ║                                      │
│  ║    Thoát           ║                                      │
│  ╚════════════════════╝                                      │
│  Phiên bản 0.6.21              ↑↓ chọn · Enter · Esc         │
└──────────────────────────────────────────────────────────────┘
```

- Cuộn: 480×424 tại `78/176`, hai trục gỗ trên/dưới, giấy da có vân, viền mực.
- Logo 58 px, tagline 20 px, cùng cột trái với cuộn.
- Menu: `118/272`, rộng 400; mục thường 54 px chữ mực, mục chính 92 px có dấu sáp đỏ;
  focus tô dải đỏ đậm, mũi tên kem.
- Tướng: scale ×4, khung 300, `bottom: 62`, tâm x 895 và 1115; bệ 210 px; đường đá từ giữa
  xuống góc phải.
- Màn chờ: con dấu cổng (cổng + vòng tròn nét đứt) ở nửa trên cuộn, dòng nhấn phím màu mực đỏ
  ở `118/452`.

## Màu

| Vai trò | Mã | Ghi chú |
|---|---|---|
| Nền ink | `#070b10` | nền ngoài, viền nút |
| Nền cỏ | `#0c1713` → `#070f0c` | tối dần xuống đáy |
| Vàng | `#e8c574` | logo, viền focus, kim cương |
| Vàng sẫm | `#a8874a` | viền nút, gradient logo |
| Chữ kem | `#f2e6c9` | chữ nút |
| Chữ mờ | `#b9b29c` | phụ đề, phím tắt |
| Đỏ chính | `#c04a3e` → `#7e2b2b` | nút Tiếp tục, dấu sáp |
| Đá | `#383a44` → `#0f1218` | mặt cổng, bậc |
| Giấy da | `#efe3c2` → `#cbb98f` | cuộn giấy (C) |
| Mực | `#3a2b1c` / `#7e2b2b` | chữ và dấu trên giấy (C) |
| Rune kiếm sĩ | `#d94a4a` | bệ trái |
| Rune pháp sư | `#8b5cf6` | bệ phải |

## Chữ

- **VT323** (OFL), phủ đủ tiếng Việt: `ế ụ ậ Ả ư ợ đ`.
- Cỡ: logo 62/96/58; tiêu đề nút 26–32; phụ 18; phím tắt 18; tagline 18–22.
- Không dùng chữ dưới 18 px trong khung; không dùng font hệ điều hành trong khung game.

## Chuyển động

| Thành phần | Nhịp |
|---|---|
| Nhân vật idle | 4 frame, 0,76 s, `steps(4)` (scale 4 và 5 có keyframe riêng) |
| Vòng rune | xoay 0,35 rad/s, nhấp nháy theo pha từng điểm |
| Sương | trôi ngang 46 s |
| Logo | thở nhẹ 5,5 s (chỉ đổi glow) |
| Đuốc (A) | lửa 0,5 s `steps(3)` |
| Màn chờ | nhấp nháy 1,5 s `steps(2)` |
| Vào menu | trượt 14 px, 0,28 s `steps(4)` |
| Focus | caret nhấp nháy 0,9 s |

`still=1` tắt animation/transition để chụp ảnh; `prefers-reduced-motion` tắt toàn bộ.

## Phím và tiếp cận

- `↑` `↓` / `W` `S`: đổi mục; `Enter` / `Space`: xác nhận; `Esc`: về màn chờ.
- `Tab` / `Shift+Tab` cũng đổi mục (không nhảy ra khỏi khung game).
- Chuột: hover đổi focus, click xác nhận; mọi thứ làm được chỉ bằng bàn phím.
- Nút là `<button>` thật, có `aria-label`; focus có viền + caret + đổi nền, không chỉ đổi màu.
- Vùng an toàn 64 px mỗi cạnh: A (cổng, tướng, bệ), B (logo, tướng, dải menu), C (cuộn, tướng)
  đều nằm trong. Dòng phiên bản/phím tắt cố ý ở ngoài (thông tin phụ, không tương tác).

## Đưa vào Godot

Mỗi phương án là một hướng khác nhau, không phải một bộ thông số chung:

- **A**: thêm `GateFrame` vẽ mặt cổng + vòm + bậc bằng `_draw` (`FrontArt`), logo đặt trong lintel,
  menu là `VBox` 360 px đặt trong vòm; hai `SpriteSheet` scale 4 đứng hai bên.
- **B**: logo góc trái, `HBoxContainer` menu ở đáy (mục chính 300×96), hai tướng scale 5 cạnh nhau
  giữa màn; thông tin phụ chuyển lên góc phải trên.
- **C**: `NinePatch`/`StyleBoxTexture` cho cuộn giấy, menu là `VBox` chữ mực trên cuộn, tướng đứng
  bên phải; cần thêm style focus nền đỏ và dấu sáp.
- Cả ba: bỏ chữ 14 px, tối thiểu 18 px; giữ `Esc`/`Enter` như hiện tại; kiểm bằng
  `gamekit ui-shots bach-ai 00-title` rồi soi từng vùng ×2.

## Tham khảo

| Nguồn | Học gì | Tránh gì | Quyết định |
|---|---|---|---|
| [Vampire Survivors Wiki · Main menu](https://vampire.survivors.wiki/w/Main_menu) + ảnh menu gốc (tải trực tiếp) | Màn đầu là **"PRESS TO START"** rồi mới vào menu; menu chính một cột nút, các mục phụ tách lên thanh trên; key art là nền lớn chứ không phải khung trang trí. | Menu nhiều mục khi mới chơi; nút phụ chen hàng với nút chính; nền coi là chỗ dán chữ. | Giữ `gate` → `menu`, một hành động chính. A biến kiến trúc thành khung; B đưa menu thành dải ngang; C đưa menu vào vật thể. |
| [Wandr · Game Menu Design](https://www.wandr.studio/blog/game-menu-design) | Menu chính phải đưa người chơi vào game nhanh, độ sâu menu nông, điều hướng controller/touch thiết kế từ đầu. | Menu nhiều tầng, thao tác chỉ làm được bằng chuột. | Một tầng menu, `↑↓ Enter Esc` đủ dùng ở cả ba phương án. |
| [StraySpark · Game UI/UX Principles](https://www.strayspark.studio/blog/game-ui-ux-design-principles) | Test **chỉ bằng controller**: mọi phần tử phải tới được, mọi hành động phải có phản hồi. | Phản hồi quá nhiều hoặc không có phản hồi. | Focus có caret + viền + đổi nền; toast ngắn; không hiệu ứng thừa. |
| [Apple WWDC 2017 · 811](https://developer.apple.com/videos/play/wwdc2017/811/) (qua ghi chú `design/ux/front-end.md`) | Một hành động chính nổi nhất; menu 3–5 mục; ẩn "Tiếp tục" khi chưa có save. | Nhiều nút ngang hàng. | 4 mục, "Tiếp tục" là nút chính duy nhất, có tóm tắt save. |
| [`games/bach-ai/design/ux/front-end.md`](../../games/bach-ai/design/ux/front-end.md) | Luồng tiêu đề → chọn nhân vật → sảnh; thứ tự nút hiện có; icon vector cho sảnh. | Đoán bố cục không dựa vào game cùng loại. | Giữ nguyên luồng và thứ tự nút; chỉ đổi cách trình bày. |

Ghi chú: API tìm kiếm ảnh của agent trả HTTP 402 (và DuckDuckGo Images chặn bằng challenge), nên bước
tìm ảnh tự động bị bỏ qua; ảnh menu Vampire Survivors tải trực tiếp từ wiki, các nguồn còn lại là bài
phân tích/ghi chú đọc bằng `webfetch`. Ảnh tham khảo chỉ để đọc bố cục, không dùng làm asset.
