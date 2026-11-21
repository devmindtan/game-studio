#!/usr/bin/env python3
"""frost-nova-iii: tier of the frost-nova family. The drawing lives in sprite-lab/families/frost-nova.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run frost-nova-iii
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "frost-nova.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
