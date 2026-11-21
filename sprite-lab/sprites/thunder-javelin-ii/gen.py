#!/usr/bin/env python3
"""thunder-javelin-ii: tier of the thunder-javelin family. The drawing lives in sprite-lab/families/thunder-javelin.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run thunder-javelin-ii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "thunder-javelin.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
