---
name: free-agent-workloop
description: >
  Workflow chuẩn cho mọi việc đa bước khi làm bằng agent hạn chế (OpenCode/free model, ít context, không song
  song, dễ mất dấu): chia công việc thành các task nguyên tử — mỗi task tự kiểm tra và commit được, làm xong một
  cái mới sang cái kế tiếp, dừng lại và báo ngay khi tắc. English triggers: free agent, limited context, small
  tasks, incremental commits, workloop, task splitting, one change at a time.
---

# Free agent workloop

Agent free vẫn làm được việc lớn, nhưng chỉ khi việc lớn được **cắt vụn thành các task nguyên tử**, mỗi task
có thể đóng trong một lượt làm việc, tự kiểm tra được và commit riêng. Không có bước "làm hết một tính năng
R" lớn: luôn là chuỗi 5–15 bước nhỏ, mỗi bước đứng vững một mình.

> Bài học thật (2026-11-17, phiên làm slot/ải/trang bị của `games/bach-ai`): một lượt "hoàn thiện toàn bộ
bảng lobby" sinh ra 11+ lỗi chồng lên nhau (nút bị clip, tên ải bị cắt, thẻ ải tràn xuống nút Bắt đầu, parse
error làm màn hình xám). Mỗi lỗi chỉ lộ ra khi chạy và xem ảnh, chứ không lộ trong unit test.

## Quy tắc chia task

Một task là **nguyên tử** khi thỏa đủ:

1. **Một thay đổi logic duy nhất** (sửa một bug, thêm một field, một màn hình, một test).
2. **Tự chứng minh được** trong một lệnh/một shot (test, `gamekit shot`, `bash -n`, `gamekit art run`).
3. **Có thể commit riêng** mà không phụ thuộc task sau vẫn dở.
4. **Nếu vượt quá**: > 1 file không liên quan, > ~30 phút, cần quyết định kiến trúc mới, hoặc phải "ước lượng"
   đáp án — thì **cắt tiếp** thành nhỏ hơn, hoặc dừng và hỏi người dùng.

## Vòng lặp mỗi task

1. **Đọc phạm vi** trước khi sửa: file bị call tới đâu tới đó (`graphify` nếu có), `LESSONS.md`, và ảnh hiện trạng.
2. **Viết kiểm tra trước** (nếu là sửa lỗi): test fail trước khi sửa, chứng minh đúng lỗi.
3. **Sửa nhỏ nhất có thể** hiện thực đủ tiêu chí trên — không "tiện tay" dọn phần khác.
4. **Chạy kiểm tra hẹp** (`gamekit test <g>`, hoặc `python3 -m py_compile`, hoặc shot). Nếu đỏ, dừng và sửa,
   không sang task khác.
5. **Xem bằng mắt** nếu thay đổi nhìn thấy: `gamekit shot` rồi **đọc ảnh gốc** (bản đầy đủ + crop phóng to vùng
   lỗi). Không kết luận "ổn" khi chưa xem; không kết luận khi chỉ mới thấy màn hình xanh/empty (parse error ra
   nền xám/đều).
6. **Commit ngay** bước đã xanh (một task = một commit). Xem `git diff --cached --stat`, commit kèm đường dẫn.
7. **Cập nhật danh sách bước** (todo): đánh dấu xong, mới bắt đầu cài đặt bước kế.

## Dấu hiệu phải dừng lại và báo

- Test/shot vẫn đỏ sau 2 lần sửa cho cùng một lỗi.
- Cần thông tin/quyền/quyết định của người dùng (đổi thiết kế, thêm dependency, xóa dữ liệu).
- Phát hiện việc hỏng ở **phạm vi ngoài** task đang làm (ghi lại, không tự ý sửa lan).
- Không nhìn được ảnh/không chạy được game → nói rõ "đã chạy nhưng chưa soi mắt được", không nói "đã kiểm tra xong".

## Mẫu danh sách bước nhỏ

```
[ ] 1. Viết test hồi quy cho X (fail)
[ ] 2. Sửa X ở <file>, test xanh
[ ] 3. Shot khu vực Y, soi ảnh, crop 2x
[ ] 4. Commit
[ ] 5. Task kế tiếp
```

## Cách gộp task

- Chỉ gộp khi lý thuyết và code **cùng một thay đổi** (VD thêm field + test của field đó).
- Không gộp "sửa bug + refactor"; không gộp "feature + unknown UI"; không gộp bước chưa kiểm tra.

## Làm cho UI/game

Mọi bước nhìn thấy được đều lặp: sửa → **chạy game/shot** → **xem ảnh + crop phóng to vùng lỗi** → sửa tiếp.
UI-shot toàn màn không đủ để bắt clip/căn giữa/tràn chữ; crop từng vùng ×1.5–×2. Xem `ui_layout_rules_test.gd`
dễ loại bỏ lỗi layout bằng máy trước khi soi bằng mắt.
