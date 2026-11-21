#!/usr/bin/env python3
"""void-orb-v: tier of the void-orb family. The drawing lives in sprite-lab/families/void-orb.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run void-orb-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "void-orb.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
