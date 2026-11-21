#!/usr/bin/env python3
"""sword-slash-iv: tier of the sword-slash family. The drawing lives in sprite-lab/families/sword-slash.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run sword-slash-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "sword-slash.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
