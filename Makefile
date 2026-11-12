# Contributor entry point for `actinf_policy_entanglement_lean`.
#
# Every target delegates to `scripts/gate.py`, which is the single definition
# of each gate arm — the GitHub Actions workflow calls the very same arms, so a
# local run and CI cannot drift. `python scripts/gate.py --list` prints the
# catalogue; `docs/guides/gate.md` documents the arms and the measured wall
# times.
#
# Pre-commit-equivalent: `make lint format types test-fast`.

GATE := uv run --no-sync python scripts/gate.py

.PHONY: help ci lint format types test-fast test-lean test-sim test-full test-all \
        slow build-lean build-mathlib-proofs mathlib regression docs gnn pipeline \
        pipeline-pdf pipeline-release pipeline-serial pdf validate-pdf readiness clean

help:
	@echo "Gate arms (all delegate to scripts/gate.py):"
	@echo "  make ci                 # lint + format + types + pipeline (the CI job)"
	@echo "  make lint               # ruff check"
	@echo "  make format             # ruff format --check"
	@echo "  make types              # mypy src/ scripts/"
	@echo "  make test-fast          # pytest -m 'not requires_pymdp and not slow'"
	@echo "  make test-full          # pytest -m 'not slow'"
	@echo "  make test-sim           # pytest -m 'requires_pymdp' (needs 'uv sync --group sim')"
	@echo "  make test-lean          # alias of test-fast"
	@echo "  make test-all           # alias of test-full"
	@echo "  make slow               # pytest -m 'slow' (Lean + MathlibProofs builds)"
	@echo "  make build-lean         # lake build + scripts/build_lean.py budget gate"
	@echo "  make mathlib            # scripts/build_mathlib_proofs.py release build"
	@echo "  make build-mathlib-proofs # alias of mathlib"
	@echo "  make regression         # scripts/regression_gate.py"
	@echo "  make docs               # hyperlink audit + generated-docs freshness"
	@echo "  make gnn                # pinned upstream GNN parser conformance"
	@echo "  make pipeline           # full scripts/run_all.py"
	@echo "  make pipeline-pdf       # run_all.py --with-pdf"
	@echo "  make pipeline-release   # run_all.py --with-pdf --with-mathlib"
	@echo "  make pipeline-serial    # legacy serial run_all.py"
	@echo "  make pdf                # render the combined PDF"
	@echo "  make validate-pdf       # validate PDF text, TeX, log, and margins"
	@echo "  make readiness          # pdf arms + ci arm + generated readiness report"
	@echo "  make clean              # remove .pytest_cache / .ruff_cache / .mypy_cache"

ci:
	$(GATE) ci

lint:
	$(GATE) lint

format:
	$(GATE) format

types:
	$(GATE) types

test-fast:
	$(GATE) test-fast

test-lean: test-fast

test-full:
	$(GATE) test-full

test-all: test-full

test-sim:
	$(GATE) test-sim

slow:
	$(GATE) slow

build-lean:
	$(GATE) build-lean

mathlib:
	$(GATE) mathlib

build-mathlib-proofs: mathlib

regression:
	$(GATE) regression

docs:
	$(GATE) docs

gnn:
	$(GATE) gnn

pipeline:
	$(GATE) pipeline

pipeline-pdf:
	$(GATE) pipeline-pdf

pipeline-release:
	$(GATE) pipeline-release

pipeline-serial:
	$(GATE) pipeline-serial

pdf:
	$(GATE) pdf

validate-pdf:
	$(GATE) pdf-validate

readiness:
	$(GATE) readiness

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
