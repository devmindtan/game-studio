#!/usr/bin/env python3
"""stomp-i: tier of the stomp family. The drawing lives in sprite-lab/families/stomp.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run stomp-i
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "stomp.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
