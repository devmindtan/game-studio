#!/usr/bin/env python3
"""earthquake-rift-v: tier of the earthquake-rift family. The drawing lives in sprite-lab/families/earthquake-rift.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run earthquake-rift-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "earthquake-rift.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
