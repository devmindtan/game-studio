#!/usr/bin/env python3
"""lightning-strike-iv: tier of the lightning-strike family. The drawing lives in sprite-lab/families/lightning-strike.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run lightning-strike-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "lightning-strike.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
