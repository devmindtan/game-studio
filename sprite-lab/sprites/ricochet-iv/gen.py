#!/usr/bin/env python3
"""ricochet-iv: drawn by sprite-lab/families/ricochet.py. Chạy: gamekit art run ricochet-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "ricochet.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
