#!/usr/bin/env python3
"""net-v: drawn by sprite-lab/families/net.py. Chạy: gamekit art run net-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "net.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
