#!/usr/bin/env python3
"""hawk-pet-i: drawn by sprite-lab/families/hawkpet.py. Chạy: gamekit art run hawk-pet-i
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "hawkpet.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
