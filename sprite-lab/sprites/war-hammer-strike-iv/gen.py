#!/usr/bin/env python3
"""war-hammer-strike-iv: tier of the war-hammer-strike family. The drawing lives in sprite-lab/families/war-hammer-strike.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run war-hammer-strike-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "war-hammer-strike.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
