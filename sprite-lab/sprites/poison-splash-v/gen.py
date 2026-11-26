#!/usr/bin/env python3
"""poison-splash-v: drawn by sprite-lab/families/poison.py. Chạy: gamekit art run poison-splash-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "poison.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
