#!/usr/bin/env python3
"""charged-shot-v: drawn by sprite-lab/families/chargedshot.py. Chạy: gamekit art run charged-shot-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "chargedshot.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
