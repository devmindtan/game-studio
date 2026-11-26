#!/usr/bin/env python3
"""hunter-mark-iii: drawn by sprite-lab/families/huntermark.py. Chạy: gamekit art run hunter-mark-iii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "huntermark.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
