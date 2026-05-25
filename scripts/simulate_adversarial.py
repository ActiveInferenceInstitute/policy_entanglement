#!/usr/bin/env python3
r"""Run the shipped adversarial-perturbation sweep.

Thin orchestrator: adversarial mathematics live in
:mod:`simulation.adversarial`; plotting and runner logic live in
:mod:`visualizations.adversarial_plots`. This script binds output
directories and forwards to the runner. The ``DATA_DIR`` / ``FIG_DIR``
module-level attributes are patchable for deterministic test runs
(``tests/test_simulate_btai_adversarial.py``).

For each scenario the runner records the measured KL drift
``D_KL(q_lambda || q_lambda^{J+dJ})``, the first-order analytical
Lipschitz bound ``lambda * epsilon * Var_q(J)^{1/2}``, their ratio,
and whether the first-order bound holds.

**Honest scope (no over-claim).** The first-order Lipschitz bound is a
*loose* small-perturbation estimate (see
``tests/test_adversarial.py::test_first_order_bound_holds_in_small_epsilon_regime``,
which allows a 10x slack); the sweep is reported descriptively. The
``bound_holds_fraction`` is a genuine observable of how far into the
epsilon grid the linearization remains a valid upper bound — it is not
a tuned scientific threshold.

Emits:

* ``output/data/adversarial_sweep.json`` — scalar summary plus per-scenario rows.
* ``output/figures/adversarial_sweep.png`` — three-panel bound-ratio figure.
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

from visualizations import adversarial_plots as _adv  # noqa: E402

# Re-exports for test access (`tests/test_simulate_btai_adversarial.py`).
_plot_adversarial = _adv._plot_adversarial

DATA_DIR = PROJECT_ROOT / "output" / "data"
FIG_DIR = PROJECT_ROOT / "output" / "figures"


def main() -> int:
    return _adv.run(data_dir=DATA_DIR, fig_dir=FIG_DIR)


if __name__ == "__main__":
    sys.exit(main())
