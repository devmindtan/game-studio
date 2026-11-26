#!/usr/bin/env python3
"""blade-orbit-ii: drawn by sprite-lab/families/bladeorbit.py. Chạy: gamekit art run blade-orbit-ii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "bladeorbit.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
