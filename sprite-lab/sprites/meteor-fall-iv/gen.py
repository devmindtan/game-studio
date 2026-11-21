#!/usr/bin/env python3
"""meteor-fall-iv: tier of the meteor-fall family. The drawing lives in sprite-lab/families/meteor-fall.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run meteor-fall-iv
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "meteor-fall.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
