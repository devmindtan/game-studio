#!/usr/bin/env python3
"""earth-strike-ii: tier of the earth-strike family. The drawing lives in sprite-lab/families/earth-strike.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run earth-strike-ii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "earth-strike.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
