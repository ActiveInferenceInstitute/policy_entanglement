# Gate entry point — arms, CI mapping, measured wall times

One entry point, [`../../scripts/gate.py`](../../scripts/gate.py), defines every
gate arm. The GitHub Actions workflow
([`../../.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) calls those
arms directly and the `make` targets are thin aliases, so a local run and CI
execute the same command — there is no second copy of a gate command to drift.

```bash
make ci                     # the `ci` job: lint + format + types + pipeline
make test-fast              # fast local loop
make gnn                    # the `gnn-conformance` job
python scripts/gate.py --list   # the arm catalog
python scripts/gate.py lint types   # several arms in one process
```

Arms run with the interpreter that launched `gate.py` (`uv run --no-sync python
scripts/gate.py …` selects the environment locally and in CI), print the exact
command they execute, and report each command's wall time. The first failing
arm stops the run and returns its exit code.

## Arms

| Arm | Command | Notes |
|---|---|---|
| `lint` | `ruff check src/ scripts/ tests/` | |
| `format` | `ruff format --check src/ scripts/ tests/` | |
| `types` | `mypy src/ scripts/` | |
| `test-fast` | `pytest -q --no-cov -m "not requires_pymdp and not slow"` | no `sim` group, no Lean builds |
| `test-sim` | `pytest -q --no-cov -m requires_pymdp` | needs `uv sync --group sim` |
| `test-full` | `pytest -q -m "not slow"` | whole suite short of the Lean release probes |
| `slow` | `pytest -q -m slow` | Lean toolchain build test + MathlibProofs axiom audit |
| `build-lean` | `scripts/build_lean.py` | `lake build` + sorry/axiom/unsafe budget |
| `mathlib` | `scripts/build_mathlib_proofs.py` | release build + axiom audit |
| `regression` | `scripts/regression_gate.py` | compares against `scripts/regression_baseline.json` |
| `docs` | `pytest --no-cov tests/test_project_wide_hyperlinks.py tests/test_docs_no_stale_registry_numbers.py tests/test_generate_index.py` | this repository has no mkdocs build; the hyperlink audit is its documentation check |
| `gnn` | pinned upstream parser conformance | see below |
| `pipeline` | `scripts/run_all.py` | Lean budget → artifacts → manuscript validation → regression gate |
| `pipeline-pdf` | `scripts/run_all.py --with-pdf` | |
| `pipeline-serial` | `scripts/run_all.py --serial` | legacy serial order |
| `pipeline-release` | `scripts/run_all.py --with-pdf --with-mathlib` | |
| `pdf` | `scripts/build_pdf.py` | Pandoc → `pandoc-crossref` → XeLaTeX/BibTeX; the preamble loads `DejaVuSans`/`DejaVuSansMono`, so a host without those fonts fails the render at the `fontspec` step |
| `pdf-validate` | `scripts/validate_pdf.py` | text, TeX, LaTeX log, margins |
| `ci` | `lint` + `format` + `types` + `pipeline` | the `ci` workflow job |
| `readiness` | `pipeline-pdf` + `pdf-validate` + `ci` + `scripts/readiness_report.py` | `make readiness` |

Selection is marker-based, using the markers declared in
[`../../pyproject.toml`](../../pyproject.toml):

- `requires_pymdp` marks the `inferactively-pymdp` surface (`sim` group).
- `slow` marks the Lean toolchain build (`tests/lean/test_lean_build.py`) and
  the MathlibProofs axiom audit
  (`tests/test_mathlib_axiom_audit.py::test_keystones_are_foundational_only_on_the_automatic_path`).

The `pipeline` arm passes `-m "not slow"` to the regression gate's pytest run
through `PYTEST_ADDOPTS` (unless the caller already set it); the pipeline's
first stage already runs `scripts/build_lean.py`, so the Lean build is enforced
without running the toolchain probe a second time.

## CI mapping

| Workflow job key | Display name | Arms |
|---|---|---|
| `ci` | "Pipeline gates, lint, and Lean budget" | `lint`, `format`, `types`, `pipeline` |
| `gnn-conformance` | "gnn conformance (pinned)" | `gnn` |

Both jobs install `uv` with `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2`
(v10.3.3). The workflow does not use the estate composite action
`ActiveInferenceInstitute/.github/.github/actions/setup-python-uv`.

`ci` syncs `uv --frozen --group sim`; `gnn-conformance` syncs `uv --frozen`
(default groups only), because the conformance test needs `numpy` and the
project's own `gnn` package, not the pymdp/JAX stack.

## GNN conformance arm

The `gnn` arm is the conformance job's only definition of the check; see
[`../../.github/GNN.md`](../../.github/GNN.md) for what it parses. It:

1. reads the canonical pin [`../../gnn/upstream.json`](../../gnn/upstream.json)
   (schema `gnn-importer-pin/v1`, `v5.0.3` at
   `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`) through
   `gnn.upstream.load_upstream_pin`, then checks `.github/GNN.md` for the pin
   path, pinned revision (full or first twelve characters), workflow filename,
   and conformance job key. Missing/unreadable pointers and omitted facts fail;
2. provisions a gate-owned checkout outside the working tree —
   `$XDG_CACHE_HOME/policy_entanglement/gnn-upstream/<tag>-<commit>/`, or
   `$GATE_CACHE_DIR` — and refuses a tag that no longer resolves to the pin.
   `$POLICY_ENTANGLEMENT_GNN_ROOT` is different: it names a checkout that may
   belong to another repository (an upstream clone or a mirror), so it is
   validated **read-only** — the commit must already be present, an existing tag
   must still peel to the pin, and its `.venv` must already import `numpy`,
   `defusedxml` and `psutil`. The arm never runs `git init`, fetch, checkout,
   `remote set-url`, or a dependency install in an explicitly selected
   checkout; anything missing is refused with instructions to fetch or prepare
   it there, or to unset the variable and let the gate use its cache;
3. gives the gate-owned checkout its own interpreter with `numpy`, `defusedxml`
   and `psutil`;
4. runs `pytest -q tests/test_gnn_upstream_conformance.py` with
   `POLICY_ENTANGLEMENT_GNN_ROOT` and `ACTINF_SKIP_BOOTSTRAP` set, then prints
   and (under GitHub Actions) records `gnn-version=… commit=…`. The canonical
   release assertion and checkout/tag checks remain the pin-drift checks.

The [GNN-FEP prerequisite](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/main/docs/workflows/gnn-fep.md#prerequisite-the-reader-ships-in-a-revision-not-in-a-version-name)
requires this interim local-reader state because the current pin has no
`gnn.importers` module. The arm does not call that absent module, vendor its
source, or substitute a newer live checkout. Shared-reader cutover must accompany
a reviewed pin advance to a release containing the reader, with deletion of the
local reader and its pin-shape tests in that same change.

A cold cache needs network access; a warm cache is offline-safe.

## Measured wall times

One run per arm, this host (Darwin arm64, Python 3.12.16, uv 0.13.7), with the
`sim` group installed and a warm `uv`/ruff/mypy cache. The estate runs other
repositories' suites on this machine concurrently, so absolute times drift by
tens of percent between runs; the columns below are single observations, not
benchmarks.

| Arm | Before this change | After this change |
|---|---|---|
| `lint` (`ruff check`) | 0.1 s (`uvx ruff check`) | 0.4 s (`gate.py lint`) |
| `format` (`ruff format --check`) | 0.1 s (`uvx ruff format --check`) | 0.4 s (`gate.py format`) |
| `types` (`mypy`) | 0.4 s (`uv run mypy`) | 0.9 s (`gate.py types`) |
| `docs` | 2.1 s (hyperlink audit only) | 23.5 s cold / 7.4 s warm (hyperlink audit + stale-registry scan + generated-index freshness) |
| `gnn` | 2.5 s (test only, `POLICY_ENTANGLEMENT_GNN_ROOT` pointing at an existing checkout with a prepared virtualenv) | 14.7 s cold (fetch + venv + dependency install + test), 3.6 s warm |
| `test-fast` | not measured cleanly (see below) | 687.5 s, exit 0 |
| `test-full` | 349.5 s, exit 1 (stale artifact stamps and an undocumented constant) | 715.1 s, exit 0 |
| `pipeline` (`run_all.py`) | not measured — exceeded the 10-minute arm bound on this host (artifact generation plus the coverage regression gate; aborted while the regression gate's pytest was at 8 min 33 s) | same bound, not measured |
| `pipeline` stages excluding the regression gate (`run_all.py --skip regression_gate`) | not measured | 375.2 s (19 stages, all outputs validated) |
| `pdf` | — | 142.2 s and 176.6 s on two runs (38 rendered sections → combined PDF) |
| `pdf-validate` | — | 2.4 s (exit 0) |

These are historical timing samples. Current test counts, pass/skip splits,
and coverage come from `output/reports/test_results.json`, not this table.

`test-full` is **not** faster in this table: 349.5 s before, 715.1 s after. The
after run happened while other repositories' suites were saturating this host,
and the same selection was observed at 590.5 s and 698.8 s in other runs, so
the delta is load, not the gate. The claim this change supports is structural
and boundedness, not throughput: the default arms no longer launch the
MathlibProofs build (that probe alone exceeded the 10-minute bound here, which
is why the old `make test-lean` and `make test-all` hung) and no longer carry
eight hand-maintained deselect entries.

`test-fast` before this change was the Makefile's eight-deselect list plus
`--ignore=tests/lean`; the unmodified arm was killed by an unrelated signal at
54 s and the clearest later observation of that selection was aborted at the
10-minute bound, so no clean "before" number exists for it. After this change
it is one marker expression.

The `uvx` command in the "before" column is also the drift this change
removes: `uvx ruff` resolves ruff independently of the locked environment,
while CI ran `uv run --no-sync ruff`, so a local lint pass did not certify the
same ruff build CI used.

`make pdf` needs `pandoc`, `pandoc-crossref`, `xelatex` and `bibtex` on `PATH`,
plus TeX Live's `dejavu` font package (the preamble sets
`\setmonofont{DejaVuSansMono}`). A TinyTeX install without it fails the render
at the `fontspec` step with `The font "DejaVuSansMono" cannot be found`;
`tlmgr install dejavu` supplies it.

## Verification order on a fresh commit

Figure artifacts embed the commit they were generated at and the output gates
compare that stamp with `HEAD`, so the pipeline must regenerate them after each
commit before the test arms are meaningful:

```bash
make ci            # pipeline regenerates figures/artifacts at the current HEAD
make test-full
make docs
make gnn
```
