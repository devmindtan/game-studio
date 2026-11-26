#!/usr/bin/env python3
"""execute-v: drawn by sprite-lab/families/roguefx.py. Chạy: gamekit art run execute-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "roguefx.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
