# Free tools (Ruff + gdtoolkit)

Install (once, local):

    python3 -m venv tools/free-tools/venv
    tools/free-tools/venv/bin/pip install --upgrade ruff gdtoolkit

Both under `venv/` (gitignored: `/tools/free-tools/venv/`). Nothing here is publishable.

## What was approved (and why)

| Tool | License | Use | Why |
|---|---|---|---|
| Ruff 0.17.5 | MIT | lint Python pipeline scripts | fast, single binary, catches real bugs (dead branch in `earth-strike-i/gen.py`, `subprocess` without `check=`) |
| gdtoolkit 4.5.0 (gdlint) | MIT | lint GDScript | long-lived, stable; catches ordering/naming issues the Godot parse+run pipeline finds late |
| gdUnit4 | MIT | **not adopted** | existing `gamekit test` already fails on parse error and SCRIPT ERROR |
| Rust linter `gdstyle` | MIT | not installed after comparison | gdtoolkit preferred (team policy: avoid adding a Rust toolchain for a small-codebase project) |
| gdtoolkit (gdformat) | MIT | **not adopted** | formatting all sources now would churn every file in the repo; use linter-only |

## Current state (as of 2026-11-17)

- Ruff on `sprite-lab/`, `tools/gamekit/pipeline/`: 793 diagnostics, mostly
  `I001` import sorting in agent-generated `gen.py` files (not worth mass-fixing;
  459 fixable but would destroy unrelated diff history).
  - **Never pass `--fix` or `--unsafe-fixes` on `sprite-lab/sprites/*/gen.py`** — those
    files reproduce shipped sprite art; only dead-code cleanup (see finding below) is safe.
  - The only findings worth acting on are `F401` (unused imports), `F821` (undefined name),
    `F841` (unused variable), `F541` (f-strings without placeholders), plus `SUP/PLW`
    for subprocess.
- gdlint on `games/bach-ai/src/`: 133 diagnostics, mostly `class-definitions-order` and
  `max-length` (project style is 140 chars vs default 100; increase `line-length` as needed).
  Zero semantic bugs detected in what was sampled.

## How to run

```sh
# Python pipeline linter (fast)
tools/free-tools/venv/bin/ruff check sprite-lab tools/gamekit/pipeline --select F401,F841,F821,F541

# Full lint, no fix (safe, read-only)
tools/free-tools/venv/bin/ruff check sprite-lab tools/gamekit/pipeline

# GDScript linter (read-only)
cd games/<g> && ../../tools/free-tools/venv/bin/gdlint src/
```

## Next step (if adopted)

Signal-blocked rules (not enabled yet):
`gdlint` max-line-length=140 for this project; adopt `ruff format` later only if the
team agrees to a one-shot reformat.
