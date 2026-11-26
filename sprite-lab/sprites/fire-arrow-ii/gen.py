#!/usr/bin/env python3
"""fire-arrow-ii: drawn by sprite-lab/families/firearrow.py. Chạy: gamekit art run fire-arrow-ii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "firearrow.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
