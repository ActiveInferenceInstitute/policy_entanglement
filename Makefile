# Local CI parity for `actinf_policy_entanglement_lean` (round-5 P2-3-lite).
#
# Replicates the split the audit recommended for GitHub Actions:
#   - `test-lean`  always runs (no pymdp, no Ollama, no LaTeX needed)
#   - `test-sim`   gates a release (requires `uv sync --group sim`)
#   - `test-all`   union of both
#   - `lint`       ruff + mypy
#   - `build-lean` lake build + sorry/axiom budget gate
#   - `regression` `scripts/regression_gate.py` only
#   - `pipeline`   full end-to-end `scripts/run_all.py`
#
# The targets are intentionally thin wrappers: they exist so a
# contributor can replicate CI exactly without memorising the flag
# combinations.  Pre-commit-equivalent: `make lint test-lean`.

.PHONY: help test-lean test-sim test-all lint build-lean build-mathlib-proofs \
        regression pipeline pipeline-pdf pipeline-release pipeline-serial pdf validate-pdf readiness clean

help:
	@echo "Targets (round-5 P2-3-lite local CI parity):"
	@echo "  make test-lean     # pure-numpy + analytical tests (no pymdp / Ollama)"
	@echo "  make test-sim      # pymdp-requiring tests; needs 'uv sync --group sim'"
	@echo "  make test-all      # both"
	@echo "  make lint          # ruff + mypy"
	@echo "  make build-lean    # lake build + scripts/build_lean.py budget gate"
	@echo "  make build-mathlib-proofs # optional additive scaffold build"
	@echo "  make regression    # scripts/regression_gate.py (test/cov/inv/Lean)"
	@echo "  make pipeline      # full scripts/run_all.py (parallel stages 4-9)"
	@echo "  make pipeline-pdf  # full scripts/run_all.py plus PDF render/validation"
	@echo "  make pipeline-release # full pipeline plus PDF and optional MathlibProofs gates"
	@echo "  make pipeline-serial   # legacy serial run_all.py"
	@echo "  make pdf           # render combined PDF through parent template"
	@echo "  make validate-pdf  # validate PDF text, TeX, log, and margins"
	@echo "  make readiness     # release gates + generated readiness report"
	@echo "  make clean         # remove .pytest_cache / .ruff_cache / .mypy_cache"

test-lean:
	uv run pytest tests/ -q --no-cov \
		--deselect tests/test_long_horizon.py \
		--deselect tests/test_multi_k_experiments.py \
		--deselect tests/test_revertibility.py \
		--deselect tests/test_simulation_pymdp.py \
		--deselect tests/test_simulation_free_energy.py \
		--deselect tests/test_pymdp_extras.py \
		--deselect tests/test_pymdp_viz.py \
		--deselect tests/test_invariants_and_dashboard.py \
		--ignore=tests/lean

test-sim:
	@echo ">>> ensure 'uv sync --group sim' has been run"
	uv run pytest tests/ -q --no-cov -m requires_pymdp

test-all:
	uv run pytest tests/ -q --ignore=tests/lean

lint:
	uvx ruff check src/ scripts/ tests/
	uvx ruff format --check src/ scripts/ tests/
	uv run mypy src/ scripts/

build-lean:
	uv run python scripts/build_lean.py

build-mathlib-proofs:
	uv run python scripts/build_mathlib_proofs.py

regression:
	uv run python scripts/regression_gate.py

pipeline:
	uv run python scripts/run_all.py

pipeline-pdf:
	uv run python scripts/run_all.py --with-pdf

pipeline-release:
	uv run python scripts/run_all.py --with-pdf --with-mathlib

pipeline-serial:
	uv run python scripts/run_all.py --serial

pdf:
	uv run python scripts/build_pdf.py

validate-pdf:
	uv run python scripts/validate_pdf.py

readiness:
	uv run python scripts/run_all.py --with-pdf --with-mathlib
	uv run python scripts/validate_pdf.py
	uv run pytest tests/ --cov=src --cov-fail-under=95
	uvx ruff check src/ scripts/ tests/
	uvx ruff format --check src/ scripts/ tests/
	uv run mypy src/ scripts/
	uv run python scripts/readiness_report.py

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
