#!/usr/bin/env python3
"""Máy GPU dùng chung của workspace (desktop-kndgm60: Windows + WSL, GTX 1660 SUPER 6 GB).

Mỗi dịch vụ chỉ bind 127.0.0.1 trong WSL; một tiến trình SSH vừa chạy `<dir>/run.sh` ở foreground vừa
chuyển cổng về loopback của laptop, nên không mở gì ra tailnet. Card 6 GB chỉ chứa một model nặng một lúc.
Viết lại bằng Python (chỉ stdlib) từ tools/gpu-host/gpu-host.cjs của 20-repo-generate-video, giữ nguyên
cách làm: `.gpu/host.json` ngoài Git, một vòng SSH để dò trạng thái, lease để người cuối cùng ra thì dừng.
"""

import argparse
import base64
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SERVICES = {
    # Cổng 8189 ở WSL để không đụng ComfyUI của 20-repo-generate-video (8188, ~/imagegen-gpu).
    "comfyui": {
        "label": "ComfyUI",
        "dir": "~/gameart-gpu",
        "remote_port": 8189,
        "local_port": 8190,
        "health": "/system_stats",
    }
}
SSH = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]


class ConfigError(Exception):
    pass


def state_dir(root):
    return Path(root) / ".gpu"


def config(root=ROOT):
    root = Path(root)
    file = state_dir(root) / "host.json"
    if not file.exists():
        raise ConfigError(f"chưa cấu hình máy GPU: thiếu {file.relative_to(root)} (chạy: tools/gpuhost/gpuhost init)")
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ConfigError(f"{file.relative_to(root)} không phải JSON hợp lệ: {e}")
    host = data.get("host", "")
    if not re.fullmatch(r"[A-Za-z0-9._@-]+", host):
        raise ConfigError('host.json: "host" phải là tên máy SSH, ví dụ desktop-kndgm60')
    services = {}
    for sid, base in SERVICES.items():
        s = {**base, **(data.get("services") or {}).get(sid, {})}
        if not re.fullmatch(r"[A-Za-z0-9._/~-]+", s["dir"]):
            raise ConfigError(f"host.json: services.{sid}.dir phải là thư mục trong WSL, ví dụ {base['dir']}")
        port = s["local_port"]
        if not isinstance(port, int) or port < 1024 or port == s["remote_port"]:
            raise ConfigError(f"host.json: services.{sid}.local_port phải khác {s['remote_port']}, ví dụ {base['local_port']}")
        services[sid] = {**s, "id": sid, "url": f"http://127.0.0.1:{port}/",
                         "pid_file": state_dir(root) / f"{sid}-tunnel.pid",
                         "log": state_dir(root) / f"{sid}.log",
                         "leases": state_dir(root) / "leases"}
    return {"host": host, "services": services}


def service(root, sid):
    services = config(root)["services"]
    if sid not in services:
        raise SystemExit(f"Dịch vụ GPU không có: {sid} (có: {', '.join(services)})")
    return services[sid]


def remote_argv(cmd):
    """argv sau `ssh <host>` để chạy `cmd` bằng bash -l trong WSL.

    Windows OpenSSH mở bằng cmd: nháy kép/&/; trong lệnh bị cmd hiểu sai (bài học 2026-11-21). Lệnh đi dưới
    dạng base64 (chỉ A-Za-z0-9+/=), gói trong một cặp nháy kép, giải mã rồi chạy trong WSL.
    """
    b64 = base64.b64encode(cmd.encode()).decode()
    return ["wsl", "-e", "bash", "-c", f'"echo {b64} | base64 -d | bash -l"']


def ssh(c, cmd, timeout=30):
    """Chạy `cmd` bằng bash trong WSL của máy GPU. Trả CompletedProcess, hoặc None nếu không gọi được ssh."""
    try:
        return subprocess.run(["ssh", *SSH, c["host"], *remote_argv(cmd)],
                              capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def read_state(body):
    if not isinstance(body, dict) or not isinstance(body.get("system"), dict) or not isinstance(body.get("devices"), list):
        return {"state": "occupied"}
    device = (body["devices"] or [{}])[0]
    return {"state": "ready", "version": body["system"].get("comfyui_version"),
            "device": device.get("name") or "cuda"}


def probe(s, timeout=1.5):
    url = urllib.parse.urljoin(s["url"], s["health"])
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = json.loads(r.read(20000) or b"null")
    except (urllib.error.URLError, OSError, ValueError):
        return {"state": "off"}
    return read_state(body)


def remote_state(root=ROOT):
    """Một vòng SSH: máy có bật không, dịch vụ đã cài chưa, cổng của nó có đang chạy không."""
    try:
        c = config(root)
    except ConfigError as e:
        return {"reachable": False, "reason": str(e)}
    cmd = "; ".join(["ss -ltnH"]
                    + [f"test -x {s['dir']}/run.sh && echo INSTALLED:{s['id']}" for s in c["services"].values()]
                    + ["true"])
    r = ssh(c, cmd, timeout=15)
    if r is None or r.returncode != 0:
        return {"reachable": False, "reason": f"không kết nối được {c['host']}"}
    installed, running = {}, {}
    for sid, s in c["services"].items():
        installed[sid] = f"INSTALLED:{sid}" in r.stdout.splitlines()
        running[sid] = re.search(rf"127\.0\.0\.1:{s['remote_port']}\s", r.stdout) is not None
    return {"reachable": True, "installed": installed, "running": running}


def pick(sid="comfyui", gpu=False, local=False, root=ROOT, check=remote_state):
    """Việc này nên chạy ở đâu. --gpu bắt buộc máy GPU (báo lỗi thay vì chuyển), --local bắt buộc laptop."""
    if gpu and local:
        raise SystemExit("Chọn một trong --gpu hoặc --local.")
    if local:
        return {"machine": "local", "reason": "chọn --local"}
    st = check(root)
    busy = [k for k, v in st.get("running", {}).items() if k != sid and v]

    def no(reason):
        if gpu:
            raise SystemExit(f"Không dùng được máy GPU: {reason}.")
        return {"machine": "local", "reason": reason}

    if not st.get("reachable"):
        return no(st.get("reason") or "máy GPU không bật")
    if not st.get("installed", {}).get(sid):
        return no(f"máy GPU chưa cài {SERVICES[sid]['label']}")
    if busy:
        return no(f"máy GPU đang chạy {SERVICES[busy[0]]['label']} (card 6 GB chỉ chứa một model)")
    return {"machine": "gpu", "reason": "máy GPU đang bật"}


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def tunnel_pid(s):
    try:
        pid = int(s["pid_file"].read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return pid if pid > 0 and alive(pid) else None


def acquire(s, name):
    s["leases"].mkdir(parents=True, exist_ok=True)
    (s["leases"] / f"{s['id']}-{name}").write_text(time.strftime("%Y-%m-%dT%H:%M:%S"), encoding="utf-8")


def holders(s):
    if not s["leases"].is_dir():
        return []
    names = []
    for path in s["leases"].iterdir():
        name = path.name
        if not name.startswith(f"{s['id']}-"):
            continue
        who = name[len(s["id"]) + 1:]
        if not who.isdigit() or alive(int(who)):
            names.append(name)
        else:
            path.unlink(missing_ok=True)  # người giữ lease đã chết
    return names


def start(sid="comfyui", lease=None, root=ROOT):
    c = config(root)
    s = c["services"][sid]
    st = remote_state(root)
    if not st.get("reachable") or not st.get("installed", {}).get(sid):
        raise SystemExit(f"máy GPU chưa sẵn sàng cho {s['label']}: {st.get('reason') or s['dir'] + '/run.sh thiếu'}"
                         " (xem tools/gpuhost/README.md)")
    if st.get("running", {}).get(sid) and not tunnel_pid(s):
        # còn bản chạy mồ côi (tunnel đã chết, vd WSL sập): dừng để trả RAM/VRAM rồi mở lại có tunnel
        ssh(c, f"{s['dir']}/stop.sh", timeout=60)
    acquire(s, lease or str(os.getpid()))
    now = probe(s)
    if now["state"] == "ready":
        return {**now, "url": s["url"]}
    if now["state"] == "occupied":
        raise SystemExit(f"Cổng {s['local_port']} ở máy này đang chạy ứng dụng khác.")
    child = None
    if not tunnel_pid(s):
        s["log"].parent.mkdir(parents=True, exist_ok=True)
        log = s["log"].open("a", encoding="utf-8")
        child = subprocess.Popen(
            ["ssh", *SSH, "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30",
             "-L", f"127.0.0.1:{s['local_port']}:127.0.0.1:{s['remote_port']}",
             c["host"], *remote_argv(f"{s['dir']}/run.sh")],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        log.close()
        s["pid_file"].write_text(str(child.pid), encoding="utf-8")
    for _ in range(360):
        time.sleep(0.5)
        st = probe(s)
        if st["state"] == "ready":
            return {**st, "url": s["url"]}
        if child is not None and child.poll() is not None:
            raise SystemExit(f"Không mở được {s['label']} trên {c['host']}. Xem {s['log']}.")
    raise SystemExit(f"{s['label']} trên {c['host']} chưa sẵn sàng sau 3 phút. Xem {s['log']}.")


def stop(sid="comfyui", root=ROOT):
    """Dừng dịch vụ trên máy GPU (trả VRAM) và đóng tunnel, ai còn giữ lease cũng dừng."""
    c = config(root)
    s = c["services"][sid]
    r = ssh(c, f"{s['dir']}/stop.sh", timeout=60)
    pid = tunnel_pid(s)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    s["pid_file"].unlink(missing_ok=True)
    for name in holders(s):
        (s["leases"] / name).unlink(missing_ok=True)
    remote = ((r.stdout or "") + (r.stderr or "")).strip() if r else "không gọi được ssh"
    if r is None or r.returncode != 0:
        raise SystemExit(f"Chưa dừng được {s['label']} trên {c['host']} ({remote}); dịch vụ có thể còn giữ "
                         f"RAM/VRAM. Chạy lại `gpuhost stop {sid}` khi máy GPU trả lời.")
    return {"remote": remote, "tunnel": bool(pid)}


def release(sid="comfyui", lease=None, keep=False, root=ROOT):
    """Trả lease của mình; không còn ai giữ thì dừng dịch vụ (trừ khi --keep)."""
    s = service(root, sid)
    lease = lease or str(os.getpid())
    (s["leases"] / f"{sid}-{lease}").unlink(missing_ok=True)
    left = holders(s)
    if keep or left:
        return {"stopped": False, "holders": len(left)}
    return {"stopped": True, **stop(sid, root)}


def status(root=ROOT):
    c = config(root)
    st = remote_state(root)
    out = {"host": c["host"], "reachable": bool(st.get("reachable")), "services": {}}
    for sid, s in c["services"].items():
        out["services"][sid] = {"url": s["url"], "tunnel": bool(tunnel_pid(s)), "holders": len(holders(s)),
                                "installed": st.get("installed", {}).get(sid, False),
                                "remote_running": st.get("running", {}).get(sid, False), **probe(s)}
    return out


def init(root=ROOT, host="desktop-kndgm60"):
    root = Path(root)
    file = state_dir(root) / "host.json"
    if file.exists():
        print(f"đã có {file.relative_to(root)}: {file.read_text(encoding='utf-8').strip()}")
        return
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps({"host": host}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"đã ghi {file.relative_to(root)}: {{\"host\": \"{host}\"}}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gpuhost", description="Máy GPU dùng chung cho art của workspace.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="ghi .gpu/host.json (một lần cho mỗi máy)")
    p.add_argument("--host", default="desktop-kndgm60")
    sub.add_parser("status", help="máy GPU có bật, dịch vụ đã cài, tunnel, lease")
    for name, text in (("start", "mở tunnel + chạy dịch vụ trên máy GPU"), ("stop", "dừng dịch vụ, đóng tunnel")):
        p = sub.add_parser(name, help=text)
        p.add_argument("service", nargs="?", default="comfyui")
        if name == "start":
            p.add_argument("--lease", help="tên người giữ lease (mặc định: pid tiến trình này)")
    p = sub.add_parser("release", help="trả lease; người cuối cùng ra thì dừng dịch vụ")
    p.add_argument("service", nargs="?", default="comfyui")
    p.add_argument("--lease")
    p.add_argument("--keep", action="store_true", help="không dừng dịch vụ dù không còn ai giữ")
    p = sub.add_parser("probe", help="hỏi endpoint qua tunnel")
    p.add_argument("service", nargs="?", default="comfyui")
    p = sub.add_parser("pick", help="in 'gpu' hoặc 'local' kèm lý do")
    p.add_argument("service", nargs="?", default="comfyui")
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--local", action="store_true")
    p = sub.add_parser("ssh", help="chạy một lệnh bash trong WSL của máy GPU")
    p.add_argument("command")
    a = ap.parse_args(argv)

    try:
        if a.cmd == "init":
            init(host=a.host)
        elif a.cmd == "status":
            st = status()
            print(f"host: {st['host']} ({'bật' if st['reachable'] else 'không kết nối được'})")
            for sid, s in st["services"].items():
                yes = lambda v: "có" if v else "không"  # noqa: E731
                extra = ""
                if s["state"] == "ready":
                    extra = " " + " ".join(x for x in (s.get("version"), s.get("device")) if x)
                print(f"{sid:10} {s['url']:26} {s['state']:9} cài: {yes(s['installed']):5}"
                      f" chạy trên máy GPU: {yes(s['remote_running']):5} tunnel: {yes(s['tunnel']):5}"
                      f" lease: {s['holders']}{extra}")
        elif a.cmd == "start":
            st = start(a.service, a.lease)
            extra = " ".join(x for x in (st.get("version"), st.get("device")) if x)
            print(f"{a.service} sẵn sàng ở {st['url']}" + (f" ({extra})" if extra else ""))
        elif a.cmd == "stop":
            st = stop(a.service)
            print(f"đã dừng {a.service}: tunnel={'có' if st['tunnel'] else 'không'}"
                  + (f" | {st['remote']}" if st["remote"] else ""))
        elif a.cmd == "release":
            st = release(a.service, a.lease, a.keep)
            print(f"đã trả lease; dừng dịch vụ: {'có' if st['stopped'] else 'không'} (còn {st.get('holders', 0)} lease)")
        elif a.cmd == "probe":
            print(probe(service(ROOT, a.service)))
        elif a.cmd == "pick":
            st = pick(a.service, a.gpu, a.local)
            print(st["machine"])
            print(st["reason"], file=sys.stderr)
        elif a.cmd == "ssh":
            c = config()
            r = ssh(c, a.command, timeout=120)
            if r is None:
                raise SystemExit(f"không gọi được ssh {c['host']}")
            sys.stdout.write(r.stdout)
            sys.stderr.write(r.stderr)
            return r.returncode
    except ConfigError as e:
        raise SystemExit(str(e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
