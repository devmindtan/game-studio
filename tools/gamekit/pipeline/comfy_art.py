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
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

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


# --- minifig openpose control image -------------------------------------------

OPENPOSE_COLORS = {
    "body": (255, 0, 0), "head": (255, 85, 0),
    "arm_l": (85, 255, 0), "arm_r": (0, 255, 85),
    "leg_l": (0, 85, 255), "leg_r": (85, 0, 255),
}


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
    scale = size / src
    sw = max(2, size // 64)

    def pt(p):
        return (p[0] * scale, p[1] * scale)

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
    p = sub.add_parser("workflow")
    p.add_argument("kind", choices=["keyframe", "animate"])
    a = ap.parse_args(argv)
    if a.cmd == "smoke":
        cmd_smoke(a.api)
    elif a.cmd == "keyframe":
        cmd_keyframe(a)
    elif a.cmd == "animate":
        cmd_animate(a)
    elif a.cmd == "workflow":
        cmd_workflow(a)


if __name__ == "__main__":
    main()
