"""Unit tests of gpuhost (see README.md). Không SSH, không cần máy GPU:

    python3 -m unittest discover -s tools/gpuhost -p 'test_gpuhost.py'
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gpuhost  # noqa: E402


def make_root(host_json):
    root = Path(tempfile.mkdtemp(prefix="gpuhost-test-"))
    if host_json is not None:
        (root / ".gpu").mkdir()
        (root / ".gpu" / "host.json").write_text(json.dumps(host_json), encoding="utf-8")
    return root


class ConfigTest(unittest.TestCase):
    def test_defaults(self):
        c = gpuhost.config(make_root({"host": "desktop-kndgm60"}))
        s = c["services"]["comfyui"]
        self.assertEqual(c["host"], "desktop-kndgm60")
        self.assertEqual((s["dir"], s["remote_port"], s["local_port"]), ("~/gameart-gpu", 8189, 8190))
        self.assertEqual(s["url"], "http://127.0.0.1:8190/")

    def test_override(self):
        root = make_root({"host": "gpu", "services": {"comfyui": {"dir": "~/other", "local_port": 8290}}})
        s = gpuhost.config(root)["services"]["comfyui"]
        self.assertEqual((s["dir"], s["local_port"], s["remote_port"]), ("~/other", 8290, 8189))

    def test_missing_file_names_init(self):
        with self.assertRaises(gpuhost.ConfigError) as e:
            gpuhost.config(make_root(None))
        self.assertIn("gpuhost init", str(e.exception))

    def test_rejects_bad_values(self):
        for bad in ({"host": "gpu; rm -rf /"}, {"host": "gpu", "services": {"comfyui": {"local_port": 8189}}}):
            with self.assertRaises(gpuhost.ConfigError):
                gpuhost.config(make_root(bad))


class PickTest(unittest.TestCase):
    def pick(self, state, **o):
        return gpuhost.pick(root=Path("/nonexistent"), check=lambda root: state, **o)

    def test_gpu_when_installed(self):
        self.assertEqual(self.pick({"reachable": True, "installed": {"comfyui": True}, "running": {}})["machine"], "gpu")

    def test_local_when_off(self):
        st = self.pick({"reachable": False, "reason": "không kết nối được desktop-kndgm60"})
        self.assertEqual((st["machine"], st["reason"]), ("local", "không kết nối được desktop-kndgm60"))

    def test_local_when_not_installed(self):
        st = self.pick({"reachable": True, "installed": {"comfyui": False}, "running": {}})
        self.assertEqual(st["machine"], "local")

    def test_forced_gpu_fails(self):
        with self.assertRaises(SystemExit):
            self.pick({"reachable": False, "reason": "máy GPU không bật"}, gpu=True)

    def test_local_wins(self):
        self.assertEqual(self.pick({}, local=True)["machine"], "local")


class LeaseTest(unittest.TestCase):
    def test_prunes_dead_holders(self):
        s = {"id": "comfyui", "leases": Path(tempfile.mkdtemp(prefix="gpuhost-lease-"))}
        (s["leases"] / "comfyui-999999999").write_text("dead", encoding="utf-8")
        (s["leases"] / "comfyui-batch-1").write_text("job", encoding="utf-8")
        self.assertEqual(gpuhost.holders(s), ["comfyui-batch-1"])


if __name__ == "__main__":
    unittest.main()


class RemoteArgvTest(unittest.TestCase):
    """2026-11-21: `gpuhost ssh 'python -c "import a;print(1)"'` vỡ vì lệnh bị bọc "…" cho cmd của Windows."""

    def test_quotes_survive(self):
        import base64
        cmd = 'python -c "import torch;print(1)" && echo \'x y\' | grep "x"'
        argv = gpuhost.remote_argv(cmd)
        self.assertEqual(argv[:4], ["wsl", "-e", "bash", "-c"])
        blob = argv[4]
        self.assertFalse(set('"\'&;<>^%') & set(blob.split(" ")[1]))
        self.assertEqual(base64.b64decode(blob.split(" ")[1]).decode(), cmd)


class OrphanTest(unittest.TestCase):
    """2026-11-21: WSL sập giữa chừng → `stop` vẫn in 'đã dừng' và ComfyUI (8 GB RAM) chạy mồ côi không tunnel."""

    def setUp(self):
        self.root = make_root({"host": "desktop-kndgm60"})
        self.calls = []
        self.saved = {k: getattr(gpuhost, k) for k in ("ssh", "remote_state", "probe", "acquire")}

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(gpuhost, k, v)

    def test_stop_fails_when_remote_unreachable(self):
        gpuhost.ssh = lambda c, cmd, timeout=30: None
        with self.assertRaises(SystemExit):
            gpuhost.stop("comfyui", root=self.root)

    def test_start_kills_orphan_without_tunnel(self):
        import subprocess
        def fake_ssh(c, cmd, timeout=30):
            self.calls.append(cmd)
            return subprocess.CompletedProcess([], 0, "", "")
        gpuhost.ssh = fake_ssh
        gpuhost.remote_state = lambda root=None: {"reachable": True, "installed": {"comfyui": True},
                                                  "running": {"comfyui": True}}
        gpuhost.acquire = lambda s, who: None
        gpuhost.probe = lambda s: {"state": "ready"}
        gpuhost.start("comfyui", root=self.root)
        self.assertTrue(any(cmd.endswith("/stop.sh") for cmd in self.calls), self.calls)
