#!/usr/bin/env python3
"""boomerang-v: drawn by sprite-lab/families/boomerang.py. Chạy: gamekit art run boomerang-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "boomerang.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
