#!/usr/bin/env python3
"""holy-column-iv: tier of the holy-column family. The drawing lives in sprite-lab/families/holy-column.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run holy-column-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "holy-column.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
