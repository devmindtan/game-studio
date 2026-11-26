#!/usr/bin/env python3
"""smoke-bomb-v: drawn by sprite-lab/families/roguefx.py. Chạy: gamekit art run smoke-bomb-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "roguefx.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
