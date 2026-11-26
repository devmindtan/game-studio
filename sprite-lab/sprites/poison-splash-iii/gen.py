#!/usr/bin/env python3
"""poison-splash-iii: drawn by sprite-lab/families/poison.py. Chạy: gamekit art run poison-splash-iii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "poison.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
