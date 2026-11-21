---
name: pixel-sprite
description: >
  Thiết kế, thử và đưa sprite pixel art vào game trong workspace này: nhân vật, kẻ địch, icon, vật phẩm,
  hiệu ứng, animation, sprite sheet nhiều animation, bản thử di chuyển. Mọi sprite được làm và thử trong
  Sprite Lab (sprite-lab/), không bao giờ làm thẳng trong game. Dùng khi người dùng nhờ vẽ/sửa/thử sprite,
  làm art không phải nhân vật LPC, tạo animation 2D, hoặc làm việc với LibreSprite/.ase.
  English triggers: pixel art, sprite, spritesheet, animation frames, sprite test, movement test,
  LibreSprite, Aseprite, game art, tileset, icon.
---

# Pixel sprite (game-studio)

Agent tự thiết kế bằng code (`gen.py` + `spritekit`) rồi lặp: nhìn ảnh, sửa. Không điều khiển GUI.
**Mọi sprite được làm và thử trong Sprite Lab** (`sprite-lab/`, xem `sprite-lab/README.md`). Chỉ khi một game
thật sự cần thì mới `promote` sang game đó.

> Bài học 2026-11-16 (`LESSONS.md`): một sheet pháp sư không liên quan đã bị tạo thẳng trong game đom đóm, và
> trình xem thử bị nhét vào `main.gd` của game. Giờ `gamekit art new <game> …` bị từ chối.

## Lệnh

```sh
gamekit art new <tên> [--size N]       # sprite-lab/sprites/<tên>/gen.py (mẫu nhiều animation)
gamekit art run <tên>                  # vẽ + kiểm tra metadata (frames, animation, neo)
gamekit art shot <tên> sheet           # ảnh: mọi animation cạnh nhau, đường đất, neo, khung
gamekit art shot <tên> move            # ảnh lưới 8 khoảnh khắc của bản thử di chuyển (demo)
gamekit art lab [<tên>] [sheet|move]   # mở lab để người dùng tự điều khiển
gamekit art test | check | list        # test của lab / kiểm mọi sprite / sprite nào đang ở game nào
gamekit art promote <tên> <game>       # chép strip + json vào games/<g>/assets/sprites/custom/<tên>/
gamekit art ase|open <tên>             # .ase để người chỉnh tay trong LibreSprite
```

### Nhân vật dùng pose rig (Pixelbolt)

Khi thiết kế người/nhân vật có tay chân và cầm vũ khí, ưu tiên nguồn pose có khớp và attachment để giữ tỷ lệ
cơ thể/vũ khí xuyên animation. Pixelbolt được gamekit ghim ở 0.17.0, chạy cục bộ, không cần dịch vụ ảnh:

```sh
gamekit art rig new <tên> [hero|hero-sword|knight]  # tạo <tên>.poses.json trong Sprite Lab
gamekit art rig validate <tên>                       # kiểm tra nguồn pose
gamekit art rig inspect <tên> [animation]            # xem onion-skin và diagnostics
gamekit art rig motion <tên> <walk|run> [px/s]       # kiểm tra tiếp đất/trượt chân/quỹ đạo
gamekit art rig build <tên>                          # render và nhập vào định dạng Sprite Lab
gamekit art shot <tên> sheet && gamekit art shot <tên> move
gamekit art test
```

Chốt brief cạnh nguồn: silhouette và khoảng âm, vai trò từng màu, mặt phẳng sáng, hướng nhìn, điểm neo, điểm
tiếp đất, các pose contact/compression/passing/extension, anticipation/release/recovery, timing và chỗ gắn
vũ khí. Xem ở 1x và khi phát animation; diagnostics chỉ báo chỗ cần xem, không tự xác nhận chất lượng.
Với `motion`, dùng tốc độ nhân vật thật trong game; mặc định 24 px/s chỉ để kiểm tra ban đầu.
`Pixelbolt` export thời lượng frame riêng; metadata Sprite Lab giữ nguyên bằng `durations_ms`. `art run` tự
chọn nguồn `.poses.json` nếu sprite có file đó; sprite dùng `gen.py` tiếp tục theo pipeline hiện tại.

## Quy trình (đủ các bước mới được báo xong)

1. **Chốt spec**: kích thước (16/24/32/48/64; nhân vật cao thì chừa khoảng trống phía trên cho nhảy), palette
   4–16 màu, hướng nhìn (mặc định quay phải), **điểm neo** (nhân vật đứng: giữa hai bàn chân trên mặt đất;
   vật bay: tâm thân; đạn/giọt: đầu va chạm), danh sách animation với số frame/fps/loop. Mơ hồ thì chọn mặc
   định và nói rõ. Tên animation dùng bộ chuẩn để lab và game hiểu: `idle`, `walk`/`run`/`fly`/`move`,
   `jump`, `attack`, `spell`, `hurt`, `death`.
2. **Vẽ silhouette trước** bằng ASCII map trong `gen.py` (`from_rows`, `outline`), rồi mới thêm chi tiết.
3. **Render**: `gamekit art run <tên>`. Lệnh này dừng nếu thiếu `<tên>.json`, neo nằm ngoài khung, hoặc
   animation không liền nhau. `gen.py` gọi `write_anim_meta(...)` (đã có sẵn trong mẫu); sprite một animation
   có thể dùng `write_meta`. **Nhân vật đứng trên đất** gọi `write_anim_meta(..., ground=True)`, đánh dấu
   animation rời đất bằng `"airborne": True` (nhảy). Khi đó mọi frame còn lại phải có hàng pixel thấp nhất
   (kể cả viền) nằm ngay trên điểm neo; lơ lửng hay lún đều bị `art run` từ chối (bài học 2026-11-16).
   Nhân vật nhỏ kiểu tối giản dựng nhanh bằng `sprite-lab/lib/minifig.py` (tư thế bằng số, tỉ lệ giữ nguyên;
   xem `sprites/swordsman/gen.py`, `sprites/mage/gen.py`).
4. **Xem tĩnh**: mở `sprite-lab/sprites/<tên>/preview.png` bằng công cụ đọc ảnh của agent. Mỗi animation một
   hàng. Nhiều agent không đọc được GIF động; `<animation>.gif` là cho người xem. Sửa, lặp 2–3 vòng.
5. **Thử sheet**: `gamekit art shot <tên> sheet` rồi xem ảnh. Mọi animation chân/neo nằm trên đường đất,
   khung không cắt mất hình (mũ khi nhảy, vũ khí khi vung).
6. **Thử di chuyển**: `gamekit art shot <tên> move` rồi xem ảnh lưới. Đạt khi: lật hướng không làm sprite
   xê dịch, đi/chạy có nhịp, nhảy có độ cao và bóng hợp lý, đòn đánh/phép/trúng đòn đọc được.
7. **Test**: `gamekit art test` (unit `SpriteSheet`/`SpriteAnchor` + integration mọi sprite trong lab).
8. **Commit** ở repo gốc (`sprite-lab/` thuộc repo gốc): `gen.py`, strip, json, png, preview, gif.
9. **Đưa vào game** (chỉ khi game cần): `gamekit art promote <tên> <game>` → vẽ bằng `SpriteSheet` trong code
   game → `gamekit test <g>` + `gamekit shot <g>` và **xem ảnh** → commit repo game.

Không báo "xong" khi chưa xem `preview.png`, ảnh `sheet` và ảnh `move`.

## Hiệu ứng đòn đánh / phép (hitbox)

> Bài học 2026-11-16 (`LESSONS.md`): đòn mặc định của kiếm sĩ dùng một sóng chém lớn không hợp kiếm ngắn, và
> tầm đánh gõ tay trong data game không khớp với hình.

- **Vẽ theo vũ khí**: đòn mặc định của một nhân vật có cỡ bằng tầm vũ khí của chính sprite đó (tay + lưỡi);
  sóng chém bay xa, vùng nổ lớn là nâng cấp, không phải đòn đầu.
- **Neo = điểm xoay** của hiệu ứng (vai/tay với vệt chém, tâm với vòng xoáy), không phải tâm canvas tùy tiện.
- **Mọi hiệu ứng liên quan đến chiến đấu phải có `hitbox` ngay khi thiết kế** (đòn đánh, projectile, vụ nổ,
  AOE, vùng gây/nhận hiệu ứng…) để game dùng trực tiếp, không phải thiết kế lại: truyền spec
  `{"shape": "rect"|"arc"|"circle", "center": [x, y], "active": [frame_đầu, frame_cuối], "dir_deg": d}` vào
  `export(...)`/`write_anim_meta`. Chọn hình theo **hình dạng thực tế** của animation: `rect` cho tia/cột/vệt
  thẳng kéo dài, `arc` cho quét/chém hình quạt, `circle` cho vùng tròn/nổ đều. Vùng đo từ pixel frame active
  (alpha ≥ 96, quầng mờ không tính) bởi `fit_hitbox`; `gamekit art run` từ chối hitbox lệch với pixel. Xem
  hitbox trên ảnh `gamekit art shot <tên> sheet` (đỏ = frame gây sát thương) và trên web viewer (bật "Hitbox").
- **Thân (hurtbox) của nhân vật/quái** cũng đo từ pixel: `export(..., body="move")` hoặc
  `write_anim_meta(..., body="idle")` ghi `"body"` (tâm = trọng tâm pixel đặc, bán kính = hình tròn cùng diện tích);
  `art run` từ chối `body` lệch với pixel; ảnh `sheet` vẽ thân màu xanh lá.
- Trong game: vùng trúng lấy bằng `SpriteHitbox.of(sheet, anim, điểm_vẽ, tỉ_lệ, lật)`, thân bằng
  `SpriteHitbox.body(sheet, điểm_vẽ, tỉ_lệ, lật)`, cùng điểm và tỉ lệ với lúc vẽ; data game chỉ chứa hệ số
  (sát thương, `area`), **không** chứa bán kính/tầm đánh/tâm thân gõ tay.

## Nhân vật: góc nhìn, đòn đánh, lớp (mặc giáp)

- **Góc nhìn theo quyết định của game**, ghi trong design của game. Bách Ải (2026-11-16): chỉ góc ngang, trái =
  lật; nhân vật chỉ có `idle`, `run`, `hurt`, `death`. Game cần thêm góc thì dùng `<anim>_down` / `<anim>_up`,
  cùng tỉ lệ, cùng neo, cùng đường đất. Ở góc trước/sau, tay giơ cao đi **cạnh** đầu, được vẽ trước đầu, không
  cắt ngang mặt/tóc; vũ khí luôn nối liền với bàn tay (bài học `attack_up`).
- **Đòn đánh không vẽ vào thân**: vệt chém, vụ nổ là sprite hiệu ứng riêng có hitbox. Vẽ cả hai thì game hiện hai
  vệt.
- **Nhân vật mặc được đồ thì vẽ theo lớp**: dựng bằng `minifig.draw_layers` và xuất bằng
  `sheet.export_layered(...)`. Kết quả gồm `layers/<lớp>_strip.png` (không viền), `"layers"` và `"outline"` trong
  json, `layers.png` để duyệt. `check_layers` (trong `art run`) bắt các lớp ghép lại + viền phải trùng từng pixel
  với strip. Lớp **theo ô trang bị, không sâu hơn** (`minifig.SLOTS`, ghi vào json `"slots"`; lớp nền `body` = mặt nằm trong
  `"base"`, không phải ô trang bị): `head` (giáp đầu), `chest` (giáp ngực: `chest_back` + `chest`), `arms` (giáp tay: `arms_back` + `arms_front`), `legs`
  (giáp chân: `legs_back` + `legs_front`), `weapon` (`weapon_back` + `weapon`). Phần sau/trước chỉ có khi ô đó ôm
  quanh thân (tay sau nằm dưới áo, tay trước nằm trên); một món đồ thay mọi phần của ô. Đồ mặc vẽ lại đúng các lớp của ô bằng
  **cùng tư thế** của nhân vật; game ghép bằng `SpriteSheet.compose_layers({lớp: texture})` (viền sau khi ghép).
- Xem **phóng to từng frame** của mỗi animation mới (preview cả sheet quá nhỏ để thấy lỗi tay/vũ khí).

## Hiệu ứng chiêu (luật `fx_craft`, người dùng 2026-11-18)

Hiệu ứng vùng của chiêu (nổ, bão, dậm đất…) vẽ theo chuẩn trong `games/<g>/design/gameplay-rules.md` mục
"Chuẩn vẽ hiệu ứng chiêu": khung gấp đôi + `"px_scale": 0.5`, ≥ 12 frame, có pha mở đầu → trúng (chớp + tia)
→ đọng lại → tan (dither), pha kết thúc 0,3–1,0 s, khối có mặt sáng/tối và viền tối bằng
`sprite-lab/lib/fxkit.py` (mẫu: `lib/icefx.py` `frost_nova`). Không vẽ hiệu ứng bằng vòng tròn / chấm một màu:
người dùng chê "đơn giản, không thể hiện sức mạnh". Không phóng to bằng thuật toán (Scale2x đã bị bỏ).
Test của game (`gameplay_rules_test`) chặn sprite có `px_scale` mà sai chuẩn; dashboard cảnh báo sprite cũ.

## Sinh vật (quái, thú, boss): chuẩn `creature-v1` (bắt buộc, người dùng 2026-11-19)

Đọc `sprite-lab/CREATURE_STANDARD.md` trước khi vẽ. Tóm tắt:
1. **Brief trước, vẽ sau:** `sprites/<tên>/brief.json` ghi `"standard": "creature-v1"`, cỡ, và **một dòng mô tả
   cho mỗi khung** của mỗi động tác (khung nào làm gì: thân, đầu, đuôi, tai, hàm…).
2. Độ phân giải theo cỡ (nhỏ 24–32, vừa 32–48, **boss: ít nhất một chiều ≥ 48 px**, tới 72 px; công cụ từ chối boss nhỏ hơn); khung tối thiểu: `move` 6, `attack` 6 (gồng ≥ 2,
   thu về ≥ 2), `hurt` 3, `death` 6; quái nhảy thêm `crouch` 2 + `jump` 4.
3. **Sống động, không đơ:** mỗi khung là một tư thế; thân nhấp nhô, đầu gật, đuôi/tai/áo chuyển động trễ nhịp;
   gồng phải đổi dáng thật (dựng lông, nhe nanh, mắt lóe).
4. **Dữ dằn nhưng vẫn đúng loài** (người dùng 2026-11-19: sói gắn gai lưng, lông tím, sẹo đỏ "giống con quái
   vật"): giữ dấu hiệu nhận dạng của loài thật (sói: tai nhọn to, mõm dài, bờm cổ, đuôi xù, lông xám/nâu);
   vẻ dữ đến từ tư thế (đầu hạ, nhe nanh, mắt lóe khi gồng, lông dựng **đúng chỗ**), không gắn gai lạ.
5. **Nâng cấp, không vẽ lại** sprite người dùng đã quen/duyệt (người dùng 2026-11-19, Vua Thạch Nhầy): giữ phong
   cách, hình khối và màu gốc; thêm khung chuyển tiếp và chi tiết trên nền đó. Muốn đổi phong cách thì hỏi trước.
6. **Không bịa đòn mới để lấp khung** (người dùng 2026-11-19: Vua Thạch Nhầy bị thêm đòn phun): `attack` vẽ
   đúng đòn mà quái đang có trong game (Vua: nhảy dậm); muốn thêm đòn thì hỏi trước.
7. `gamekit art run` **từ chối** sprite có brief mà thiếu động tác/khung, mô tả không khớp số khung, hoặc thân trên
   đổi < 4 % giữa các khung `move` (chỉ chân động).
8. **Dạng pha 2 / phẫn nộ phải trông dữ hơn dạng thường** (người dùng 2026-11-20: chân Cổ Thụ Trụi Lá "xấu, phải hùng
   hổ hơn"): dáng thấp và rộng, chân/tay to dồn trọng lượng, đầu gối choãi, vuốt bám đất, thân chúi tới, mặt cau
   nhe nanh. Chi mảnh, ngắn, đứng sát nhau trông ngây ngô. Chi duỗi dài nằm ngang trông như chân nhện. Thêm chân thì **giữ chiều cao thân** (nâng đỉnh thân, đừng rút đáy
   thân lên: người dùng chê "thân cụt ngủn"); tay quái dữ có vuốt nhọn (Cổ Thụ: bàn tay quỷ bằng cành sắt). Xem ở 5×
   cả 8 khung `move` trước khi báo xong.
9. **Boss đổi pha phải có animation `transform`** (≥ 8 khung, ~1,5 s, người dùng 2026-11-20: "thiếu animation chuyển
   trạng thái") trong sheet pha 2: khựng → biến hình từng bước → gầm. Chỉ chớp màu là không đủ (test
   `monster_standard_test` của bach-ai chặn). Đổi màu dần thì nháy giữa hai màu, đừng trộn màu (xanh + đỏ ra nâu bẩn).

## Chiêu nhiều bậc (I–V): một file cho cả họ

Bản vẽ của mọi bậc một chiêu nằm trong **`sprite-lab/families/<họ>.py`** (phần chung + bảng `TIERS` các số đổi theo bậc,
đánh giá 2026-11-21: các gen.py bậc trước đây là bản sao chỉ khác vài con số). Thư mục bậc (`<họ>-ii` …) giữ `gen.py`
3 dòng gọi file họ, nên `gamekit art run <họ>-iii` vẫn chạy như cũ. Sửa cả dòng chiêu: sửa file họ, chạy lại mọi bậc.
Thêm bậc: thêm một dòng vào `TIERS` và một thư mục có stub giống các bậc khác.

## Quy tắc pixel art

- **Hình đặc trưng vẽ bằng bản đồ pixel tay** (`from_rows` hoặc danh sách chuỗi): nón, mũ, đầu vũ khí, khuôn
  mặt, biểu tượng. Công thức (vòng lặp co giãn, lệch theo k²…) chỉ dùng để đặt vị trí và tạo chuyển động; dựng
  hình dáng bằng công thức cho ra bậc thang lởm chởm (bài học 2026-11-16: nón pháp sư "méo xẹo"). Cần biến thể
  (gió, nghiêng) thì vẽ thêm một bản đồ, đừng uốn bằng công thức.
- **Luật gameplay của game là điều kiện xong**: Bách Ải chốt luật ở `games/bach-ai/design/gameplay-rules.md` (số liệu
  `assets/data/gameplay_rules.json`: tự động, hitbox pixel, tầm trong màn hình, ra đòn nhanh, 4 hướng, mạnh theo
  cấp, khung nhỏ, đúng class, cân bằng DPS). Vẽ hiệu ứng cho game nào thì mở dashboard
  (`sprite-lab/serve-viewer.sh` → `games.html`, tab **Luật gameplay**, và demo ở tab **Kỹ năng**) và chỉ báo xong khi
  kỹ năng **đạt luật bắt buộc**; `gamekit test <g>` fail nếu kỹ năng trong game vi phạm.
- **Skill phải khớp gameplay Bách Ải (bắt buộc trước khi vẽ)**: đọc `games/bach-ai/assets/data/classes.json`, `upgrades_<class>.json` và cách game nạp FX trong `src/run/run.gd` (`sheets` load theo **tên sprite**, `_add_fx(sprite, anim, ...)`). Checklist:
  - **Tên sprite** phải đúng `skills.<id>.sprite` trong data. Game `sheets.get(name)` trả `null` và **bỏ qua lặng lẽ** nếu sai tên — không có lỗi để phát hiện.
  - **Animation**: đòn định hướng có `slash_right/left/up/down` (game gọi qua `_slash_anim()`); AOE/cấp bậc dùng **một animation một lần** (`burst`/`spell`, `loop:false`) đặt **neo tại tâm người chơi**; skill duy trì như `whirlwind` dùng `spin`.
  - **Hitbox** có sẵn, shape đúng hình thật, `active` nằm trong animation. Game scale sprite theo `area` rồi dùng `SpriteHitbox.of`, nên hitbox phải đo từ pixel chứ không gõ tay.
  - **Neo**: AOE/đạn ở tâm hoặc đầu va chạm; nhân vật đứng `ground=True`.
  - **Phân class theo roadmap**: băng/đất/phép thuật → Pháp sư hoặc Kiếm sĩ (`ground-slam`, `earth-spikes` là knight); tên/lõi chiêu phải khớp class đó, không vẽ skill "cho chung".
  - **Bậc I–V là 5 sprite riêng** `<skill>-i..v` để data sau này map `level → sprite`. Hiện game **chưa có mapping đó** (upgrade chỉ nhân `skill_damage.*`): khi bàn giao phải nói rõ đây là **TODO phía game**, không tự sửa `src/` hay `assets/data/` của game.

- **Chiêu thức nâng cấp I–V — chống "cùng một khuôn đổi màu"**: I–V là **nhịp tiến hóa**, KHÔNG phải bản thiết kế chung. Trước khi vẽ, phải chốt **DNA riêng của dòng chiêu** (từ nguyên tố/chất liệu) và ghi ngay vào docstring `gen.py` của cả 5 bậc, ví dụ:
  - **Băng/frost**: kết tinh, **đối xứng tròn**, cạnh sắc, phát sáng lạnh, tuyết.
  - **Đất/earth**: **đứt gãy, dịch chuyển khối, bất đối xứng, nặng**, tảng đá có mặt phẳng/đường vân, bụi, magma lộ ra — KHÔNG được là vòng tròn đối xứng kiểu băng.
  - **Lửa**: ngọn lửa liếc lên, sóng nhiệt, khói, màu nóng chảy. **Sét**: tia thẳng/gãy, chớp tức thời, điểm chạm. **Độc**: chất lỏng loang, bọt, hơi. **Ánh sáng**: chùm tia, halo, lõi trắng.
- Mỗi bậc phải thêm **một ý mới về hình/hành vi** (không chỉ palette hay kích thước), trên nền motif kế thừa (xem dưới). Cấm dùng lại cấu trúc của dòng khác (vd `vòng → hoa → cột → xoáy → mandala` cho cả băng lẫn đất). Khi thiết kế bậc nào, **render và đặt cạnh bậc tương đương của ít nhất một dòng khác**; nếu silhouette giống nhau thì đổi một trong hai trước khi commit. Ghi trong commit message dòng đã so sánh với ai.
- **Bậc sau kế thừa bậc trước** (người dùng 2026-11-17: Frost Nova III cũ thành "cọc băng", trông như một chiêu khác):
  bậc N **giữ nguyên hình đặc trưng (motif) của bậc N-1**, nhận ra ngay khi đặt cạnh nhau, rồi **thêm hoặc phát triển
  đúng một ý mới** (lớp ngoài, mảnh bắn ra, vòng thứ hai, hành vi mới của chính motif đó). Ví dụ Frost Nova:
  I vòng băng → II ngôi sao 8 cánh → III cùng ngôi sao đó + mảnh băng bắn ra từ đầu cánh → IV/V tiếp tục từ ngôi sao.
  Bậc V là bản đẹp và mạnh nhất, **không phải chiêu khác**: motif vẫn phải còn.
  **Tự kiểm trước khi commit:** ghép frame lớn nhất của cả 5 bậc thành một hàng và xem; chỉ ra được motif của bậc
  N-1 nằm ở đâu trong bậc N, không chỉ ra được thì vẽ lại. Ghi trong docstring `gen.py`: "Kế thừa: <motif bậc trước>
  + <ý mới>". Một thiết kế đẹp nhưng không kế thừa thì **tách thành chiêu riêng** (sprite tên mới, ví dụ
  `glacial-spires`), không bỏ đi. Mọi bậc có hitbox đo từ pixel, neo giữ trục, tag `tier-I`…`tier-V`, **không giữ
  bản không đánh số**.

- **Vũ khí đối xứng (kiếm, đại kiếm, dao găm) vẽ thẳng đứng**, trục là tâm lưỡi; guard/cán/pommel nằm cùng trục. **Tự kiểm tra bằng script**: với mỗi hàng, tập pixel active (alpha ≥ 96) phải khớp tập phản chiếu qua trục (mirror `x' = 2*axis - x`); xem preview trước khi báo xong. Không tự đo thì không được nói là đã xong.
- **Đường chéo đặc (lưỡi kiếm, vệt chém…) điền theo từng cột**: với mỗi cột `x`, tính tâm `y` rồi tô một
  đoạn `y` liên tiếp; vòng lặp kiểu `(x+t, y-t)` chỉ cho pixel chạm góc → nhìn như caro/đứt gãy (bài học
  2026-11-16: sword/greatsword). Guard phải **vuông góc** với trục lưỡi, cán/pommel **cùng trục** với lưỡi. Đầu lưỡi nhọn dần qua 2–3 cột (rộng 3→2→1 px), không chừa một điểm 1px đơn lẻ trông như bị teo.

- Không anti-alias, không gradient mịn; dùng màu phẳng và banding.
- 1 pixel = 1 đơn vị thiết kế; scale nguyên, nearest.
- Silhouette phải đọc được ở 1x; outline tối 1px hoặc selective outline.
- Animation: 4–8 frame cho idle/loop, 6–10 cho walk/run; đổi 1–2 pixel mỗi frame; neo cố định qua mọi frame.
- **Vũ khí dựng từ một trục** (người dùng 2026-11-20: lưỡi Chém kiếm lệch khỏi cán): kiếm/giáo/búa vẽ bằng một hàm
  nhận (chuôi, mũi) rồi tự tính cán phía sau, chắn tay vuông góc qua chuôi, lưỡi từ chuôi tới mũi (ví dụ `sword()` trong
  `sprite-lab/sprites/card-icons/gen.py`). Không đặt toạ độ từng bộ phận bằng tay. Không dùng `line(width=2)` cho vũ khí chéo:
  nó làm dày mỗi nét về một phía khác nhau; đặt từng pixel trên trục 45°, mọi phần dày về cùng một phía. Soát ảnh phóng to: lưỡi phải mọc từ
  giữa chắn tay.
- Nền trong suốt (`RGBA`), không viền quanh cả canvas.
- **Quái nhảy phải có animation nhảy** (người dùng 2026-11-18): `crouch` (lấy đà, nén) và `jump` (bật → đỉnh →
  rơi → đáp), mọi tư thế đặt chân ở hàng đất trong khung; game nâng sprite theo `hop_height` và giữ bóng.
  Test `data_consistency_test.gd` của Bách Ải chặn quái nhảy thiếu hai animation này. Vẽ sinh vật nhỏ
  (≤ 32 px) thì vẽ tay từng tư thế (ASCII); hình học (ellipse) chỉ ổn từ khoảng 48 px trở lên.
- **Sinh vật không phải người thì di chuyển bằng bộ phận của chính nó** (người dùng 2026-11-18: boss cây có "chân"
  thay vì rễ): cây trườn bằng chùm rễ, rắn uốn thân, ma lơ lửng có đuôi, nhầy co giãn. Không gắn chân người vào
  thứ không có chân; phần di chuyển phải tương phản với thân (màu/viền riêng) để đọc được ở 1x. Rễ cây là
  **nhiều rễ riêng rẽ** (5–7, đặt tay từng chiếc): to ở gốc, thon dần, xoắn, có mấu/gai, **đầu rễ cong vểnh
  lên**, dài ngắn và hướng không đều, mỗi rễ có viền tối riêng để tách nhau (người dùng 2026-11-18). Tránh:
  nét mảnh tỏa đều (chân nhện), một khối nêm hoặc gò đất liền (không thấy từng rễ). Cành/tay chĩa xuống
  chạm đất hai bên thân đọc thành chân: tư thế nghỉ để cành ngang vai, vểnh lên.

## Godot 4.7

- Vẽ bằng addon dùng chung `addons/gamekit/sprites/`:
  `SpriteSheet.load_dir(dir, name)` rồi `sheet.draw(self, anim, t, point, scale, flip_h)` trong `_draw()`.
  Bên dưới là `SpriteAnchor.dest_rect`: **không** căn theo tâm canvas, **không** tự tính lại rect khi lật
  bằng chiều rộng âm (Godot giữ vùng vẽ, chỉ lật texture).
- Pixel art cần lọc Nearest: `rendering/textures/canvas_textures/default_texture_filter=0` (game do `gamekit
  new` tạo và lab đã có). Thiếu nó, sprite bị nhòe khi phóng to.
- Export: preset phải gói `assets/sprites/*.json` (template của gamekit đã có).

## Môi trường đã kiểm chứng

- `libresprite` 1.3 ở `~/.local/bin/libresprite` (GPL-2.0). Bản 1.3 **không có MCP/HTTP/`--set`**; script
  headless chỉ vẽ được một frame, nên animation làm bằng Python. Lỗi JS in `Error:` nhưng exit code vẫn 0,
  nên luôn kiểm tra file output.
- Pillow 10.2 có sẵn; **không có numpy**.

## Không làm

- Không tạo hay thử sprite trong thư mục game; không thêm cờ xem thử sprite vào code của game.
- Không gõ số frame, fps, neo vào config của game: chúng nằm trong `<tên>.json` do `gen.py` sinh ra.
- Không dùng dịch vụ ảnh trả phí, không gửi art lên mạng.
- Không sửa `templates/` hay `tools/lpc-generator/` (clone upstream).
- Không ghi đè sprite đã promote khi chưa hỏi; sửa trong lab rồi promote lại.
- Không bỏ qua commit (`AGENTS.md`, "Quy tắc commit"): lab ở repo gốc, bản promote ở repo game.
