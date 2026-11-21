# gpuhost: chạy ComfyUI trên máy GPU

Công cụ dùng chung của workspace để chạy ComfyUI tạo art trên máy GPU `desktop-kndgm60` (Windows + WSL Ubuntu, GTX 1660 SUPER 6 GB), theo cùng pattern với `20-repo-generate-video/tools/gpu-host`.

## Vì sao không chạy local

Laptop không có CUDA (chỉ Intel Iris Xe). Đo thực tế (2026-11-21, CPU): SD1.5 512²/18 step = 202 s/ảnh, chất lượng khung tranh ở 56 px; SDXL 1024² OOM kill (19,3 GB RSS) trên 23 GB RAM. Việc nặng tạo ảnh phải chạy trên máy GPU.

## Cách nối

- Dịch vụ chỉ bind `127.0.0.1` trong WSL của máy GPU; không mở ra tailnet.
- Một tiến trình SSH vừa chạy `~/gameart-gpu/run.sh` ở foreground vừa forward `127.0.0.1:8189` (remote) về `127.0.0.1:8190` (laptop).
- Card 6 GB chỉ chứa một model nặng một lúc. Lease trong `.gpu/leases/`: người cuối cùng ra thì dừng dịch vụ, trả VRAM.
- Cấu hình `.gpu/host.json` là **local từng máy, ngoài Git** (đã gitignore `/.gpu/`).

## Dùng

```bash
tools/gpuhost/gpuhost init                  # tạo .gpu/host.json (một lần/máy)
tools/gpuhost/gpuhost status                # máy có bật, dịch vụ có cài, tunnel, lease
tools/gpuhost/gpuhost start comfyui         # mở tunnel + chạy ComfyUI trên máy GPU
tools/gpuhost/gpuhost probe comfyui         # hỏi /system_stats qua tunnel
tools/gpuhost/gpuhost release comfyui       # trả lease; người cuối cùng ra thì dừng
tools/gpuhost/gpuhost stop comfyui          # dừng ngay, trả VRAM
tools/gpuhost/gpuhost pick comfyui --gpu    # bắt buộc GPU (báo lỗi nếu không dùng được)
tools/gpuhost/gpuhost ssh 'nvidia-smi'      # chạy lệnh trong WSL máy GPU
```

## Bố trí trên máy GPU

Tách khỏi `~/imagegen-gpu` (20-repo, port 8188):

| | Giá trị |
|---|---|
| Thư mục WSL | `~/gameart-gpu` |
| Port remote | `8189` |
| Port local (tunnel) | `8190` |
| Chạy | `run.sh` → ComfyUI `--listen 127.0.0.1 --port 8189 --lowvram --reserve-vram 0.5 --fp8_e4m3fn-unet --fp8_e4m3fn-text-enc` (**không** `--cpu-vae`) |
| Dừng | `stop.sh` (chỉ kill process thuộc `~/gameart-gpu/app`) |

Model nằm trong `~/gameart-gpu/app/models/` (riêng, không dùng chung symlink `/mnt/d/...` của imagegen-gpu). Custom node trong `~/gameart-gpu/app/custom_nodes/`.

## Cấu hình đã đo (2026-11-21, GTX 1660 SUPER 6 GB, WSL 11 GB RAM)

| `run.sh` | keyframe SDXL Lightning 768², 4 step (ấm máy) | Ghi chú |
|---|---|---|
| có `--cpu-vae` | 26,3 s | decode VAE trên CPU chiếm ~2/3 thời gian |
| bỏ `--cpu-vae` | **9,3 s** | cấu hình đang dùng |
| bỏ thêm fp8 + `--lowvram` | sập | SDXL fp16 vượt 11 GB RAM của WSL, ComfyUI chạy mồ côi |

- Lần đầu sau khi bật mất thêm ~15–40 s để nạp model. Đo nhiều lần thì đổi seed: prompt trùng y hệt được ComfyUI
  cache (1,7 s, không phải tốc độ thật).
- `animate` (SD1.5 + ControlNet OpenPose + IP-Adapter, 512²/20 step): ~17 s/frame. Nhân vật theo dáng nhưng chi
  tiết (vũ khí, màu) trôi giữa các frame, nên chỉ dùng làm tham chiếu dáng, không làm frame game.

## Dùng trong quy trình sprite

`gamekit art concept <tên> "<prompt>"` tự `start`/`release` dịch vụ, tạo concept và pixel hoá (xem skill
`pixel-sprite`, bước 0). AI chỉ chốt ngoại hình; animation vẽ bằng `minifig`/rig trong Sprite Lab.

## Quy tắc

- Không tải model ComfyUI/diffusion nặng về laptop; tải lên máy GPU.
- Không đụng `~/imagegen-gpu` của 20-repo-generate-video.
- Không commit `.gpu/`, model, output sinh ra.
- Kiểm tra: `python3 -m unittest discover -s tools/gpuhost -p 'test_gpuhost.py'`.
