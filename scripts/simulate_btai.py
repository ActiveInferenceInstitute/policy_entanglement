#!/usr/bin/env python3
r"""Run the shipped Branching-Time AIF (BTAI) head-to-head baseline.

Thin orchestrator: BTAI mathematics live in :mod:`simulation.btai_baseline`,
plotting and runner logic live in :mod:`visualizations.btai_plots`.
This script binds output directories and forwards to the runner. The
``DATA_DIR`` / ``FIG_DIR`` module-level attributes are patchable for
deterministic test runs (``tests/test_simulate_btai_adversarial.py``).

**Honest scope (no over-claim).** This run *executes* the configured
harness end-to-end and emits the observables; it is a reproducible
worked run, not the full compute-matched scientific study. UCB-MCTS
estimates the lowest-EFE joint action, so the visitation posterior is
not expected to equal the *soft* analytic posterior; the KL-vs-budget
curve and exponent are reported descriptively. The planned
hypothesis (BTAI converges to the exact posterior as B_MCTS -> infty,
at a sample-complexity exponent ~1) is to be tested by the full study,
not asserted here.

Emits, when pymdp is available:

* ``output/data/btai_baseline.json`` — scalar summary plus per-budget rows.
* ``output/figures/btai_baseline.png`` — three-panel deterministic figure.

Skipped (with a stdout note, exit 0) when the ``sim`` group / pymdp is
not installed, mirroring every other ``scripts/simulate_*.py`` stage.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from _bootstrap import ensure_project_paths  # noqa: E402

ensure_project_paths(project_root=PROJECT_ROOT)

from visualizations import btai_plots as _btai  # noqa: E402

# Re-exports for test access (`tests/test_simulate_btai_adversarial.py`
# loads the script via importlib and asserts on these names; keep them
# stable).
REFERENCE_LAMBDA = _btai.REFERENCE_LAMBDA
HORIZON = _btai.HORIZON
_plot_btai = _btai._plot_btai
_build_pymdp_efe = _btai._build_pymdp_efe

DATA_DIR = PROJECT_ROOT / "output" / "data"
FIG_DIR = PROJECT_ROOT / "output" / "figures"


def main() -> int:
    return _btai.run(data_dir=DATA_DIR, fig_dir=FIG_DIR)


if __name__ == "__main__":
    sys.exit(main())
