#!/usr/bin/env python3
"""ComfyUI workflow cho art pixel (chạy trên máy GPU qua gpuhost, không local).

Hai quy trình (user 2026-11-21):
- keyframe: SDXL Lightning 4-step + LoRA pixel-art-xl -> tạo hình gốc / icon / hiệu ứng.
- animate:  SD1.5 All-In-One Pixel + ControlNet OpenPose + IP-Adapter -> frame animation
            theo khung xương minifig 48x48 (chân y=43).

Dùng qua CLI:
  python3 comfy_art.py smoke [--api URL]
  python3 comfy_art.py keyframe --prompt "..." --out out.png [--size 768]
  python3 comfy_art.py animate --ref ref.png --poses poses_dir --out frames_dir
  python3 comfy_art.py workflow keyframe|animate > wf.json

Hoặc qua gamekit: gamekit art comfy <args...>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

DEFAULT_API = "http://127.0.0.1:8190"
NEGATIVE = "blurry, photo, 3d render, text, watermark, frame, border, gradient background, bad anatomy"


# --- ComfyUI API ---------------------------------------------------------------

def _post(api: str, path: str, data: dict) -> dict:
    req = urllib.request.Request(
        api.rstrip("/") + path,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _get(api: str, path: str) -> dict:
    with urllib.request.urlopen(api.rstrip("/") + path, timeout=30) as r:
        return json.loads(r.read())


def upload_image(api: str, file_path: Path, subfolder: str = "", image_type: str = "input") -> str:
    """Upload ảnh lên ComfyUI input dir, trả về filename để dùng trong LoadImage."""
    import uuid
    boundary = f"----gameart{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in (("image_type", image_type), ("subfolder", subfolder)):
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    data = file_path.read_bytes()
    body += (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{file_path.name}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode()
    body += data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(api.rstrip("/") + "/upload/image", data=bytes(body),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["name"]


def run_prompt(api: str, prompt: dict, timeout: int = 600, poll: float = 1.5) -> dict:
    pid = _post(api, "/prompt", {"prompt": prompt, "client_id": "gameart"})["prompt_id"]
    t0 = time.time()
    while True:
        hist = _get(api, f"/history/{pid}")
        if pid in hist:
            return hist[pid]
        if time.time() - t0 > timeout:
            raise TimeoutError(f"ComfyUI prompt {pid} quá {timeout}s")
        time.sleep(poll)


def extract_images(history: dict) -> list[dict]:
    out = []
    for node_out in history.get("outputs", {}).values():
        for img in node_out.get("images", []) or []:
            out.append(img)
    return out


def download_image(api: str, image: dict, dest: Path) -> Path:
    from urllib.parse import urlencode
    qs = urlencode({"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")})
    with urllib.request.urlopen(api.rstrip("/") + "/view?" + qs, timeout=60) as r:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.read())
    return dest


# --- Workflow builders ---------------------------------------------------------

def workflow_keyframe(prompt: str, negative: str = NEGATIVE, seed: int = 7, steps: int = 4,
                      size: int = 768, lora_strength: float = 1.0,
                      filename_prefix: str = "gameart/keyframe") -> dict:
    """SDXL Lightning 4-step + LoRA pixel-art-xl: tạo hình gốc/icon/hiệu ứng."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sdxl_lightning_4step.safetensors"}},
        "2": {"class_type": "LoraLoader", "inputs": {
            "model": ["1", 0], "clip": ["1", 1], "lora_name": "pixel-art-xl.safetensors",
            "strength_model": lora_strength, "strength_clip": lora_strength}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["2", 1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": size, "height": size, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix}},
    }


def workflow_animate(reference_name: str, control_name: str, prompt: str,
                     negative: str = NEGATIVE, seed: int = 7, steps: int = 20,
                     size: int = 512, control_strength: float = 0.8,
                     ipadapter_weight: float = 0.85,
                     filename_prefix: str = "gameart/anim") -> dict:
    """SD1.5 All-In-One Pixel + ControlNet OpenPose + IP-Adapter: frame theo control image."""
    return {
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Public-Prompts-Pixel-Model.ckpt"}},
        "clip_pos": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["ckpt", 1]}},
        "clip_neg": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["ckpt", 1]}},
        "ref": {"class_type": "LoadImage", "inputs": {"image": reference_name}},
        "ctrl_img": {"class_type": "LoadImage", "inputs": {"image": control_name}},
        "cn": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_openpose_fp16.safetensors"}},
        "cn_apply": {"class_type": "ControlNetApplyAdvanced", "inputs": {
            "positive": ["clip_pos", 0], "negative": ["clip_neg", 0], "control_net": ["cn", 0],
            "image": ["ctrl_img", 0], "strength": control_strength, "start_percent": 0.0, "end_percent": 1.0}},
        "ip_load": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model": ["ckpt", 0], "preset": "PLUS (high strength)"}},
        "ip_apply": {"class_type": "IPAdapterAdvanced", "inputs": {
            "model": ["ip_load", 0], "ipadapter": ["ip_load", 1], "image": ["ref", 0],
            "weight": ipadapter_weight, "weight_type": "style transfer", "combine_embeds": "concat",
            "start_at": 0.0, "end_at": 1.0, "embeds_scaling": "V only"}},
        "latent": {"class_type": "EmptyLatentImage", "inputs": {"width": size, "height": size, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["ip_apply", 0], "positive": ["cn_apply", 0], "negative": ["cn_apply", 1],
            "latent_image": ["latent", 0], "seed": seed, "steps": steps, "cfg": 7.0,
            "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["ckpt", 2]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": filename_prefix}},
    }


def workflow_motion(prompt: str, negative: str = "", seed: int = 7, steps: int = 20, width: int = 480,
                    height: int = 480, length: int = 17, shift: float = 8.0,
                    filename_prefix: str = "gameart/motion") -> dict:
    """Wan 2.1 T2V 1.3B: clip tham khảo CHUYỂN ĐỘNG (nhịp, quán tính, đồ bay), không dùng làm frame game.

    Text encoder umt5-xxl bản GGUF Q4 (ComfyUI-GGUF) để vừa 12 GB RAM của WSL; length = 4n+1.
    """
    neg = negative or "static, blurry, low quality, text, watermark, multiple people, cropped, camera motion"
    return {
        "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.1_t2v_1.3B_fp16.safetensors",
                                                        "weight_dtype": "default"}},
        "clip": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": "umt5-xxl-encoder-Q4_K_M.gguf",
                                                            "type": "wan"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["clip", 0]}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["clip", 0]}},
        "shift": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["unet", 0], "shift": shift}},
        "latent": {"class_type": "EmptyHunyuanLatentVideo", "inputs": {
            "width": width, "height": height, "length": length, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["shift", 0], "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["latent", 0],
            "seed": seed, "steps": steps, "cfg": 6.0, "sampler_name": "uni_pc", "scheduler": "simple",
            "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": filename_prefix}},
    }


# --- minifig openpose control image -------------------------------------------

OPENPOSE_COLORS = {
    "body": (255, 0, 0), "head": (255, 85, 0),
    "arm_l": (85, 255, 0), "arm_r": (0, 255, 85),
    "leg_l": (0, 85, 255), "leg_r": (85, 0, 255),
}


POSE_KEYS = ("hip", "top", "head", "sh_back", "sh_front", "hand_back", "hand_front", "foot_back", "foot_front")


def _fit_pose(g: dict, size: int, fill: float = 0.85) -> tuple[float, float, float]:
    """scale, ox, oy để khung xương cao `fill` × ảnh, giữa theo ngang, đáy chừa lề như nhau.

    Vẽ thẳng theo canvas 48 px thì người chỉ cao ~20% ảnh và ControlNet bỏ qua pose (đo 2026-11-21).
    Đầu là một điểm nên cộng thêm nửa đầu (~4 px minifig) ở trên.
    """
    xs = [g[k][0] for k in POSE_KEYS]
    ys = [g[k][1] for k in POSE_KEYS]
    top, bottom = min(ys) - 4, max(ys)
    scale = size * fill / max(1.0, bottom - top)
    ox = size / 2 - (min(xs) + max(xs)) / 2 * scale
    oy = size * (1 + fill) / 2 - bottom * scale
    return scale, ox, oy


def openpose_from_pose(pose: dict, size: int = 512, src: int = 48) -> "Image.Image":
    """Vẽ stick figure kiểu OpenPose từ minifig geometry lên nền đen."""
    from PIL import Image, ImageDraw
    # Import minifig from sprite-lab
    here = Path(__file__).resolve()
    ws = here.parents[3]
    sys.path.insert(0, str(ws / "sprite-lab"))
    sys.path.insert(0, str(ws / "tools/gamekit/pipeline"))
    import lib.minifig as mf  # noqa: E402

    g = mf.geometry(pose)
    img = Image.new("RGB", (size, size), (0, 0, 0))
    d = ImageDraw.Draw(img)
    scale, ox, oy = _fit_pose(g, size)
    sw = max(2, size // 64)

    def pt(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    def limb(a, b, col):
        d.line([pt(a), pt(b)], fill=col, width=sw)

    def dot(p, col, r=max(2, size // 48)):
        x, y = pt(p)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    hip = g["hip"]
    top = g["top"]
    head = g["head"]
    limb(hip, top, OPENPOSE_COLORS["body"])
    limb(top, head, OPENPOSE_COLORS["head"])
    limb(g["sh_back"], g["sh_front"], (255, 85, 0))
    limb(g["sh_back"], g["hand_back"], OPENPOSE_COLORS["arm_l"])
    limb(g["sh_front"], g["hand_front"], OPENPOSE_COLORS["arm_r"])
    limb(hip, g["foot_back"], OPENPOSE_COLORS["leg_l"])
    limb(hip, g["foot_front"], OPENPOSE_COLORS["leg_r"])
    for p, c in [(head, (255, 170, 0)), (top, (255, 0, 0)), (hip, (255, 0, 85)),
                 (g["hand_back"], (85, 255, 0)), (g["hand_front"], (0, 255, 85)),
                 (g["foot_back"], (0, 85, 255)), (g["foot_front"], (85, 0, 255))]:
        dot(p, c)
    return img


# --- CLI ----------------------------------------------------------------------

def cmd_smoke(api: str):
    st = _get(api, "/system_stats")
    dev = (st.get("devices") or [{}])[0].get("name", "?")
    ver = (st.get("system") or {}).get("comfyui_version", "?")
    print(f"ok {api} comfyui={ver} device={dev}")


def cmd_keyframe(args):
    wf = workflow_keyframe(args.prompt, seed=args.seed, steps=args.steps, size=args.size,
                           lora_strength=args.lora, filename_prefix="gameart/keyframe")
    t0 = time.time()
    hist = run_prompt(args.api, wf, timeout=args.timeout)
    imgs = extract_images(hist)
    if not imgs:
        raise SystemExit("không có ảnh output")
    out = Path(args.out)
    download_image(args.api, imgs[0], out)
    print(f"{out} {round(time.time()-t0,1)}s")


def cmd_animate(args):
    """Test animation: render minifig control poses -> SD1.5+CN+IPAdapter."""
    ref = Path(args.ref)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ref_name = upload_image(args.api, ref)
    # poses: json list of minifig pose dicts, or generate a small default set
    if args.poses and Path(args.poses).exists():
        poses = json.loads(Path(args.poses).read_text())
    else:
        here = Path(__file__).resolve()
        ws = here.parents[3]
        sys.path.insert(0, str(ws / "sprite-lab"))
        sys.path.insert(0, str(ws / "tools/gamekit/pipeline"))
        import lib.minifig as mf  # noqa: E402
        poses = [mf.pose(), mf.run_pose(0), mf.run_pose(2), mf.run_pose(4), mf.run_pose(6)]
    prompt = args.prompt or "pixel art game character, full body, crisp pixels, solid dark background, centered"
    results = []
    for i, p in enumerate(poses):
        ctrl_img = openpose_from_pose(p, size=args.size)
        ctrl_path = out_dir / f"_control_{i:02d}.png"
        ctrl_img.save(ctrl_path)
        ctrl_name = upload_image(args.api, ctrl_path)
        wf = workflow_animate(ref_name, ctrl_name, prompt, seed=args.seed + i, steps=args.steps,
                              size=args.size, control_strength=args.control,
                              ipadapter_weight=args.ip_weight, filename_prefix=f"gameart/anim_{i:02d}")
        t0 = time.time()
        hist = run_prompt(args.api, wf, timeout=args.timeout)
        imgs = extract_images(hist)
        if imgs:
            dest = out_dir / f"frame_{i:02d}.png"
            download_image(args.api, imgs[0], dest)
            results.append({"frame": i, "file": str(dest), "seconds": round(time.time()-t0, 1)})
            print(f"  {dest.name} {results[-1]['seconds']}s")
    (out_dir / "manifest.json").write_text(json.dumps({"frames": results, "prompt": prompt}, indent=2))
    print(f"ok {len(results)} frames -> {out_dir}")


# --- concept: AI chỉ để chốt ngoại hình, rồi pixel hoá về đúng cỡ sprite ---------------

def pixelize(img, height: int = 30, colors: int = 12, bg_tol: int = 40):
    """Ảnh SDXL (768², 'pixel art' giả, mờ) -> sprite tham chiếu thật: nền trong suốt, nhân vật cao `height` px,
    tối đa `colors` màu, không dither.

    Ảnh gốc mờ vì "pixel" của model không khớp lưới và có chuyển màu (người dùng 2026-11-21); thu nhỏ BOX về
    đúng chiều cao sprite rồi lượng tử hoá cho ra pixel sắc, màu phẳng như sprite trong game.
    Nền = màu trung vị của viền ảnh; pixel khác nền quá `bg_tol` là nhân vật.
    """
    from PIL import Image
    im = img.convert("RGB")
    w, h = im.size
    px = im.load()
    border = [px[x, y] for x in range(0, w, 4) for y in (0, h - 1)] + \
             [px[x, y] for y in range(0, h, 4) for x in (0, w - 1)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > bg_tol:
                mp[x, y] = 255
    box = mask.getbbox()
    if not box:
        raise ValueError("không tách được nhân vật khỏi nền")
    im, mask = im.crop(box), mask.crop(box)
    # Lượng tử ở độ phân giải gốc (chỉ pixel nhân vật), rồi mỗi ô lấy màu NHIỀU NHẤT: thu nhỏ BOX trộn màu
    # nên mặt/khăn nhỏ thành màu bùn (đã thấy 2026-11-21).
    # Palette chỉ từ pixel nhân vật (nền xám từng chiếm 9/12 màu và nuốt màu da); FASTOCTREE giữ vùng màu nhỏ.
    mp = mask.load()
    ip = im.load()
    fg = [ip[x, y] for y in range(im.height) for x in range(im.width) if mp[x, y]]
    sample = Image.new("RGB", (len(fg), 1))
    sample.putdata(fg)
    palimg = sample.quantize(colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    q = im.quantize(palette=palimg, dither=Image.Dither.NONE)
    pal = q.getpalette()
    qp = q.load()
    tw = max(1, round(im.width * height / im.height))
    out = Image.new("RGBA", (tw, height), (0, 0, 0, 0))
    op = out.load()
    for ty in range(height):
        y0, y1 = ty * im.height // height, max(ty * im.height // height + 1, (ty + 1) * im.height // height)
        for tx in range(tw):
            x0, x1 = tx * im.width // tw, max(tx * im.width // tw + 1, (tx + 1) * im.width // tw)
            votes, inside, total = {}, 0, 0
            for y in range(y0, y1):
                for x in range(x0, x1):
                    total += 1
                    if mp[x, y]:
                        inside += 1
                        i = qp[x, y]
                        votes[i] = votes.get(i, 0) + 1
            if inside * 2 >= total:
                i = max(votes, key=votes.get)
                op[tx, ty] = (pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2], 255)
    return out


def palette_of(img) -> list[dict]:
    """Màu của các pixel đặc, nhiều trước: [{"hex": "#rrggbb", "count": n}]."""
    counts = {}
    for r, g, b, a in img.getdata():
        if a:
            counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
    return [{"hex": "#%02x%02x%02x" % c, "count": n} for c, n in sorted(counts.items(), key=lambda kv: -kv[1])]


def cmd_concept(args):
    """N seed -> <dir>/raw_<seed>.png (ảnh AI), <seed>.png (pixel 1x), <seed>.json (palette), sheet.png (xem)."""
    from PIL import Image
    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)
    seeds = [args.seed + i for i in range(args.seeds)]
    tiles = []
    for s in seeds:
        raw = out / f"raw_{s}.png"
        wf = workflow_keyframe(args.prompt, seed=s, size=args.size, filename_prefix="gameart/concept")
        t0 = time.time()
        imgs = extract_images(run_prompt(args.api, wf, timeout=args.timeout))
        if not imgs:
            raise SystemExit("không có ảnh output")
        download_image(args.api, imgs[0], raw)
        px = pixelize(Image.open(raw), args.height, args.colors)
        px.save(out / f"{s}.png")
        (out / f"{s}.json").write_text(json.dumps({"seed": s, "prompt": args.prompt, "height": args.height,
                                                   "palette": palette_of(px)}, indent=2) + "\n")
        tiles.append((Image.open(raw).convert("RGB"), px))
        print(f"  seed {s}: {out / f'{s}.png'} {px.width}x{px.height} {round(time.time() - t0, 1)}s")
    # sheet.png: hàng trên ảnh AI thu nhỏ, hàng dưới bản pixel phóng NEAREST cùng cỡ
    cell = 8 * args.height
    sheet = Image.new("RGB", (cell * len(tiles), cell * 2), (40, 42, 54))
    for i, (raw, px) in enumerate(tiles):
        sheet.paste(raw.resize((cell, cell)), (i * cell, 0))
        big = px.resize((px.width * 8, px.height * 8), Image.NEAREST)
        sheet.paste(big, (i * cell + (cell - big.width) // 2, cell + (cell - big.height) // 2), big)
    sheet.save(out / "sheet.png")
    print(f"ok {len(tiles)} concept -> {out / 'sheet.png'} (chọn một seed, dùng palette trong <seed>.json)")


def cmd_motion(args):
    """Clip tham khảo chuyển động -> <dir>/frame_XX.png, sheet.png (lưới frame), motion.gif (xem nhịp)."""
    from PIL import Image
    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)
    wf = workflow_motion(args.prompt, seed=args.seed, steps=args.steps, width=args.width, height=args.height,
                         length=args.length, filename_prefix="gameart/motion")
    t0 = time.time()
    imgs = extract_images(run_prompt(args.api, wf, timeout=args.timeout))
    if not imgs:
        raise SystemExit("không có frame output")
    frames = []
    for i, im in enumerate(imgs):
        dest = download_image(args.api, im, out / f"frame_{i:02d}.png")
        frames.append(Image.open(dest).convert("RGB"))
    secs = round(time.time() - t0, 1)
    cols = min(6, len(frames))
    tw = 160
    th = round(tw * frames[0].height / frames[0].width)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (40, 42, 54))
    for i, f in enumerate(frames):
        sheet.paste(f.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    sheet.save(out / "sheet.png")
    frames[0].save(out / "motion.gif", save_all=True, append_images=frames[1:], duration=1000 // 16, loop=0)
    (out / "motion.json").write_text(json.dumps({"prompt": args.prompt, "seed": args.seed, "frames": len(frames),
                                                 "size": [args.width, args.height], "seconds": secs}, indent=2) + "\n")
    print(f"ok {len(frames)} frame {secs}s -> {out / 'sheet.png'} (THAM KHẢO nhịp chuyển động, không dùng làm frame)")


def cmd_workflow(args):
    if args.kind == "keyframe":
        wf = workflow_keyframe("PROMPT", filename_prefix="gameart/keyframe")
    else:
        wf = workflow_animate("reference.png", "control.png", "PROMPT", filename_prefix="gameart/anim")
    json.dump(wf, sys.stdout, indent=2)
    sys.stdout.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="comfy_art", description="ComfyUI pixel-art workflow qua gpuhost")
    ap.add_argument("--api", default=DEFAULT_API)
    ap.add_argument("--timeout", type=int, default=600)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("smoke")
    p = sub.add_parser("keyframe")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--steps", type=int, default=4)
    p.add_argument("--size", type=int, default=768)
    p.add_argument("--lora", type=float, default=1.0)
    p = sub.add_parser("animate")
    p.add_argument("--ref", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--poses")
    p.add_argument("--prompt")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--size", type=int, default=512)
    p.add_argument("--control", type=float, default=0.8)
    p.add_argument("--ip-weight", type=float, default=0.85)
    p = sub.add_parser("concept", help="chốt ngoại hình: N ảnh AI -> sprite tham chiếu pixel + palette")
    p.add_argument("--prompt", required=True)
    p.add_argument("--dir", required=True)
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--seed", type=int, default=101)
    p.add_argument("--size", type=int, default=768)
    p.add_argument("--height", type=int, default=30, help="chiều cao nhân vật (px) trong sprite")
    p.add_argument("--colors", type=int, default=12)
    p = sub.add_parser("motion", help="Wan 1.3B: clip tham khảo chuyển động (không phải frame game)")
    p.add_argument("--prompt", required=True)
    p.add_argument("--dir", required=True)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--width", type=int, default=480)
    p.add_argument("--height", type=int, default=480)
    p.add_argument("--length", type=int, default=17)
    p = sub.add_parser("workflow")
    p.add_argument("kind", choices=["keyframe", "animate"])
    a = ap.parse_args(argv)
    if a.cmd == "smoke":
        cmd_smoke(a.api)
    elif a.cmd == "keyframe":
        cmd_keyframe(a)
    elif a.cmd == "animate":
        cmd_animate(a)
    elif a.cmd == "concept":
        cmd_concept(a)
    elif a.cmd == "motion":
        if (a.length - 1) % 4:
            raise SystemExit("--length phải là 4n+1 (17, 21, 33…)")
        cmd_motion(a)
    elif a.cmd == "workflow":
        cmd_workflow(a)


if __name__ == "__main__":
    main()
