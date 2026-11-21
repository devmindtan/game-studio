#!/usr/bin/env python3
"""solar-ray-v: tier of the solar-ray family. The drawing lives in sprite-lab/families/solar-ray.py (one file per family,
review 2026-11-21); this stub runs it for this folder. Chạy: gamekit art run solar-ray-v
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[2] / "families" / "solar-ray.py"), init_globals={"TIER_FILE": __file__},
               run_name="__main__")
