#!/usr/bin/env python3
"""fireball-blast-v: tier of the fireball-blast family. The drawing lives in sprite-lab/families/fireball-blast.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run fireball-blast-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "fireball-blast.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
