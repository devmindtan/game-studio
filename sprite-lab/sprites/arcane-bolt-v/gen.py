#!/usr/bin/env python3
"""arcane-bolt-v: tier of the arcane-bolt family. The drawing lives in sprite-lab/families/arcane-bolt.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run arcane-bolt-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "arcane-bolt.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
