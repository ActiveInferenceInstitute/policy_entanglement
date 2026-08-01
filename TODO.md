# TODO — Policy Entanglement in Active Inference (`actinf_policy_entanglement_lean`)

**Status:** Active — review passes complete; all Minor/Medium findings implemented and all
previously-scoped Major findings (M1, M2) implemented this continuation. No item remains
deferred.

**Owner:** Daniel Ari Friedman (daniel@activeinference.institute)

**Last reviewed:** 2026-08-01 (deepest hostile red-team review; implementation pass + completion pass)

---

## Current status

The repository passed a **deepest hostile red-team review** (root README/AGENTS/ISA/CHANGELOG
orientation → full-tree review → real-suite + lint measurement → parallel 3-axis subagent
audit → implement-all-Minor/Medium → re-verify). Headline measured state **on this tree after
the fix pass** (real values, from `uv run python -m pytest tests/ --cov=src`):

- `1464 + 4 previously-failing` → **1474 passed, 7 skipped, 1 xfailed** after the first fix batch;
  the full-suite run after the S0-1/S0-3 integrity closures is **1478 passed, 7 skipped,
  1 xfailed**; the final run (adding the M1/M2 Major closures — `run_captured_bounded` + Plotly
  vendoring) is **1480 passed, 7 skipped, 1 xfailed** (suite green; the 4 clean-tree failures
  from session start are FIXED — see Completed). Added **10 new regression tests** this review.
- Aggregate `src/` coverage measured **94.79%** in the sim-enabled venv. **This is a documented
  rotating-project exception, not a regression**: with the pymdp `sim` group installed, the
  pymdp-gated simulation surface (`src/simulation/{agents,inference,multi_k_experiments,
  revertibility,rollout,robustness,long_horizon,sweep}.py`) is reachable-but-thinly-covered and
  drags aggregate coverage below the 95% gate — the exact basis documented in `pyproject.toml`
  `[tool.coverage]`. The ≥95% figure holds in the reproducible gate environment WITHOUT the
  `sim` group. **This pass did not regress coverage**: the untouched tree measures 94.83% in the
  same environment; the implemented fixes plus their regression tests net ~neutral (94.80%).
  All five `CRITICAL_COVERAGE_MODULES` floors are met (status 95.05%, pdf_validation 96.13%,
  metadata 97.85%, parameter_sweep 96.97%, btai_plots 97.85%).
- `ruff check` + `mypy` both **0 errors** on `src/`, `scripts/`, `tests/`.
- No interrupted source state; working tree contains only the intentional review-pass changes
  (see `git diff`).

---

## Completed / Closed

Everything below was fully implemented and verified this pass (2026-08-01). No item in this
section remains open.

### Clean-tree suite failures fixed (3 root causes / 4 tests)

- **[x] `tests/test_meta_files_and_float_residual.py` — stale hard-coded membership set.**
  `MANUSCRIPT_NON_BODY_MD` (source) gained `00_abstract.md` (the release-workflow symlink) in
  an earlier commit, but the test's `expected` frozenset was never updated, so the suite was red
  on a clean tree. Fix: synced the test set to the source constant and pinned
  `00_abstract.md` explicitly. File: `tests/test_meta_files_and_float_residual.py`.
- **[x] `tests/test_python_api_coverage.py` — undocumented public identifiers.**
  `src/manuscript/publication_metadata.py` exports `CANONICAL_VERSION_DOI` and
  `CANONICAL_VERSION_RECORD` (added in the Zenodo version-DOI release) that were not listed in
  `docs/reference/python_api_manuscript.md`, failing `test_every_public_identifier_documented`.
  Fix: documented both constants in the API reference. Files: `docs/reference/python_api_manuscript.md`.
- **[x] `tests/test_validation_cli_gate.py` (2 tests) — stale PDF path literal.**
  `docs/guides/zenodo-doi-strategy.md` referenced the old template destination
  `../template/output/actinf_policy_entanglement_lean/pdf/`, which the stale-literal scanner
  flags (`output/actinf_policy_entanglement_lean(?:/|_combined\.pdf)`). Fix: updated the
  `cp` destination to the canonical `output/pdf/actinf_policy_entanglement_lean_combined.pdf`.
  Files: `docs/guides/zenodo-doi-strategy.md`.

### Correctness / robustness fixes (RedTeam subagent Task 1)

- **[x] `src/simulation/inference.py` — VFE uses the state prior `D` as the policy prior `E_k`.**
  `_variational_free_energy_from_parts` computes `E_q[log E_k]` from `spec.streams[k].D`
  (`num_states`) even though the VFE formula's prior is over policies (`num_controls`). This is
  only valid when `num_states == num_controls` (true for every production builder, which use
  uniform 2-state/2-action streams). Fix: fail-fast `ValueError` with an explanatory message when
  a stream's `num_controls != num_states`, so a mis-sized stream can never silently produce a
  wrong VFE. Regression test added. Files: `src/simulation/inference.py`,
  `tests/test_simulation_free_energy.py`.
- **[x] `src/simulation/statistics.py` — `pymdp_summary_statistics` silently assumed an
  ascending-λ sweep.**
  Field semantics (`lambda_min`, `lambda_max`, `*_at_lambda_max`, `kl_to_lambda_zero_*`) index
  `bundles[0]`/`bundles[-1]`; an unsorted/reversed caller sweep mislabelled manuscript variables
  with no error. Fix: raise `ValueError` when `lams` is not non-decreasing. Regression test added.
  Files: `src/simulation/statistics.py`, `tests/test_statistics_pure.py`.
- **[x] `src/lean/free_energy.py` — `kl_divergence` accepted a negative entry in the reference.**
  A negative `p` entry coinciding with `q>0` returned a garbage finite KL instead of
  failing/inf. Fix: raise `ValueError` on `any(p < 0)`. Regression test added.
  Files: `src/lean/free_energy.py`, `tests/test_free_energy.py`.
- **[x] `src/simulation/metrics.py` — `half_saturation_interpolated` lacked length / min-size
  validation.**
  It indexes `lams[j]`/`tcs[j]` directly; a length mismatch or single-point sweep could
  mis-pair or index out of bounds. Fix: raise `ValueError` on length mismatch and on `size < 2`.
  Two regression tests added. Files: `src/simulation/metrics.py`, `tests/test_statistics_pure.py`.
- **[x] `src/lean/spectral.py` — default Schmidt `atol` contradicted the documented guidance.**
  `schmidt_rank` / `schmidt_decomposition` defaulted to `1e-12`, while `src/AGENTS.md` documents
  `1e-9` (the Ising posterior's small singular value is ~1e-10, so `1e-12` mis-grades a
  near-mean-field joint as rank 2). Production callers already pass the deliberate value; this
  fix aligns the library default via a shared named constant `SCHMIDT_RANK_DEFAULT_ATOL = 1e-9`.
  Regression test added. Files: `src/lean/spectral.py`, `tests/test_spectral.py`.

### Security / integrity / reproducibility fixes (RedTeam subagent Task 0)

- **[x] `src/gates/regression_pytest.py` + `regression_gate.py` — stale-positive invariant
  certification closed.**
  The gate certified `invariants N/M ≥ floor` from a gitignored count file with no freshness
  bind. The invariants file embeds a `git rev:` provenance line; the gate now fails-closed when
  that embedded rev differs from current HEAD (absent/`unknown` provenance is left to the count
  floor). Regression tests: fresh-ok / stale-fail / no-provenance-skip / gate-level stale-fail.
  Files: `src/gates/regression_pytest.py`, `src/gates/regression_gate.py`,
  `tests/test_regression_gate.py`.
- **[x] `src/manuscript/output_gates/png_validation.py` — stale figure certification closed.**
  PNG `check_png` validated structure but never bound the embedded `project.git_revision` to
  current HEAD (only the writer's `git rev` was present-but-unenforced). Fix:
  `check_png_git_revision` fails on an embedded rev != HEAD (and on non-rev garbage); absent /
  `unknown` provenance skips (structural validation owns that path). Regression test added.
  Files: `src/manuscript/output_gates/png_validation.py`, `tests/test_output_gates.py`.
- **[x] `src/lean/build_gate.py` — non-portable locale-default reads.**
  Lean source read with `.read_text()` (locale encoding) in 4 scanner loops. Fix: explicit
  `encoding="utf-8"`.
- **[x] `src/manuscript/` — non-portable locale-default reads.**
  18 `.read_text()`/`json.loads(…read_text())` calls across 12 files read without an explicit
  encoding; on a non-UTF-8 locale these could `UnicodeDecodeError` or mangle content. Fix:
  explicit `encoding="utf-8"` everywhere.
- **[x] `src/gates/regression_gate.py` — env-override bypass printed no staleness warning.**
  `REGRESSION_GATE_USE_EXISTING_TEST_REPORT=1` certified the stored report with no warning that
  a fresh pytest/coverage snapshot was skipped. Fix: prominent warning on use, telling the
  operator to verify `generated_at`.
- **[x] `src/lean/mathlib_proofs_gate.py` — unbounded network `lake exe cache get`.**
  The Mathlib cache hydration is a network download with no timeout; a stalled download hangs
  `run_all` indefinitely. Fix: `_MATHLIB_CACHE_TIMEOUT_SECONDS = 1800`; on
  `subprocess.TimeoutExpired` control falls through to the existing `lake build` fallback (so a
  legit build is never blocked).
- **[x] `src/orchestration/build_pdf.py` — PDF subprocesses had no hang bound.**
  pandoc / bibtex / xelatex ran forever if the toolchain stalled. Fix:
  `_PDF_SUBPROCESS_TIMEOUT_SECONDS = 3600` (generous; only catches true hangs).

### Docs / claim-provenance fixes (RedTeam subagent Task 2)

- **[x] `src/manuscript/variables_pipeline.py` + `AGENTS.md` — "22/22 lake jobs" misrepresented
  as a live tool read.**
  `lean_lake_jobs_total` is a pinned constant (build_gate does not parse a job count); the docs
  claimed "Live summary from scripts/build_lean.py". Fix: explicit source comment documenting the
  pin and the real live check (the regression gate's lake-job floor), and reworded the AGENTS row.
- **[x] `README.md` — scaffold-count mismatch (`~21` vs code-pinned `20`).**
  The Lean-honesty table said "~21" filler re-exports while code pins 20. Fix: aligned the row to
  `~20` so the honesty ledger agrees with the source-derived count.
- **[x] `src/orchestration/run_all.py` — "re-run-and-bit-match determinism" over-claim.**
  The manifest docstring claimed a bit-match determinism audit that PNGs/timestamps can't
  satisfy. Fix: reworded to "content audit of generated artifacts".
- **[x] `src/orchestration/build_pdf.py` — dead no-op `if subs == 0: pass`.**
  Removed the empty branch (the `re.subn` already handles both outcomes) and documented intent.
- **[x] `manuscript/INDEX.md` — stale row for the `00_abstract.md` symlink.**
  `generate_index.py` excludes `MANUSCRIPT_NON_BODY_MD`; now that `00_abstract.md` is in that
  set, the regenerated index correctly drops its row. Verified against source
  (`index_generator.py:105`).

### Regression tests added (all real arrays, no mocks)

- `test_statistics_pure.py`: unsorted-sweep rejection; interpolated half-sat length mismatch;
  interpolated half-sat single-point rejection.
- `test_free_energy.py`: `kl_divergence` negative-reference rejection.
- `test_spectral.py`: Schmidt default-atol alignment (1e-9).
- `test_simulation_free_energy.py`: VFE state/control-dim mismatch rejection.
- `test_regression_gate.py`: invariants fresh-ok / stale-fail / no-provenance-skip; gate-level
  stale-invariant fail-closed.
- `test_output_gates.py`: PNG embedded-git-revision bind to HEAD (matching / absent / unknown /
  garbage / stale).

## Completion pass — continued review (2026-08-01)

The two remaining **Major** findings from the previous pass were implemented and
verified this continuation, so nothing stays deferred. Each entry below is the
Major finding followed by how it was closed.

### M1. Local build / pytest subprocesses lacked a bound on captured output — CLOSED

- **Finding:** `subprocess.run(..., capture_output=True)` on the long-running local builds
  (`lake build`, full `pytest`, `run_all._spawn`) had no cap on captured output and no timeout.
  A hung/chatty child could stall the pipeline or balloon memory via an unbounded `PIPE`.
  Affected `src/lean/build_gate.py`, `src/gates/regression_pytest.py:163,225`,
  `src/orchestration/run_all.py:161,175`.
- **[x] Fix:** new memory-capped runner `gates.regression_pytest.run_captured_bounded` streams
  stdout/stderr to a temp file, keeps only the final tail (`_MAX_CAPTURED_CHARS = 2_000_000`)
  and enforces a generous hang timeout (`_GATE_PYTEST_TIMEOUT_SECONDS = 7200`). It now backs the
  local pytest snapshot, the Lean budget snapshot, and `run_all._spawn`'s captured path. Regression
  tests cover output capping, exit-code surfacing, and timeout kill.

### M2. Interactive dashboard loads Plotly from a CDN at view time — CLOSED

- **Finding:** `output/web/dashboard.html` referenced `https://cdn.plot.ly/plotly-2.35.2.min.js`;
  the headline interactive deliverable broke offline. Version pinned but not vendored.
  Affected `src/reporting/_interactive_dashboard_fallback.py`.
- **[x] Fix:** the parser now accepts an optional `plotly_js` payload;
  `render_interactive_dashboard_html(..., plotly_js=...)` inlines a vendored copy for a fully
  offline-capable page, and falls back to the documented CDN tag when no payload is supplied.
  `vendored_plotly_js()` provides an **opt-in** fetch (only when `REPORTING_VENDOR_PLOTLY` is
  set, with retry + timeout + size cap), so default builds and tests stay deterministic and
  network-free. Regression tests cover the inline path and the CDN fallback.

---

## Major — Scoped (deferred)

**None.** All validated Major findings from the deepest review are implemented (see the
completion-pass section above). No Major remains deferred.

---

## Notes

- **No-mock policy, deterministic seeds, thin-orchestrator discipline:** all fixes respect the
  repo's AGENTS.md constitution (real `numpy` arrays, `np.random.default_rng(seed=…)`, business
  logic in `src/`, thin `scripts/`).
- **Coverage honesty:** the 94.79% figure above is the measured value with the `sim` group
  installed and is NOT a regression (baseline 94.83% in the same environment); the ≥95% gate is
  met in the reproducible no-sim environment per `pyproject.toml`'s documented rotating-project
  exception. Do not re-certify a higher number without re-measuring in the gate environment.
- **Verification took ~20 min** for the full suite (Lean boundary `lake build` cold); subsequent
  runs are faster once output/ + .lake are warm.
