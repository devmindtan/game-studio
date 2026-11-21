#!/usr/bin/env python3
"""sword-wave-iv: tier of the sword-wave family. The drawing lives in sprite-lab/families/sword-wave.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run sword-wave-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "sword-wave.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
