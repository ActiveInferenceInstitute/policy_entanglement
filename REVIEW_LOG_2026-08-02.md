# Documentation deep review — 2026-08-02

## Scope

Reviewed the repository documentation surfaces: root README / AGENTS /
CONTRIBUTING, `docs/` (index, guides, styleguide fragments, module pages,
reference pages, simulation pages, audit reports), `manuscript/` docs and
registry READMEs, Lean/source-adjacent READMEs and AGENTS files, `scripts/`
and `tests/` docs, citation/license metadata (CITATION.cff, LICENSE,
`.aii/config.yaml`, `domain_profile.yaml`), and repository-local links.
Generated `output/` artifacts and dependency caches were treated as
disposable and were not edited.

## Preflight

- Branch: `main`; default remote branch: `origin/main`.
- Working tree was clean and already up to date with `origin/main`; no fast-forward was needed.
- No `.github/` directory or environment files were present.
- Repository hyperlink regression test: passed before and after the pass (`1 passed`).
- No local absolute paths or credential-looking values found in any documentation.
- Generator output confirms 17 Lean submodules, 76 theorem/lemma declarations,
  39 definitions, 11 structures, 126 total declarations, 21 theorem-registry rows —
  the root README snapshot is numerically accurate.

## Findings and implementation record

### Minor (7)

- `.aii/config.yaml`: citation DOI value contained leaked Markdown-link syntax;
  corrected to a plain scalar (`62cf243`).
- `CITATION.cff`: no `version`/`date-released`; added `version: "1.0"` and
  `date-released: "2026-05-27"` matching `manuscript/config.yaml` and the Zenodo
  v1.0.0 deposit (`62cf243`).
- `README.md`: Citation block used a non-canonical title; aligned to the
  CITATION.cff / config.yaml title (`5b50f5c`).
- `docs/README.md`: incomplete citation-metadata sentence; orphaned
  `docs/RELEASE_v1.0.0.md` now linked from the cross-cutting list (`793e49b`).
- `docs/guides/README.md`: stale 60%/90% coverage wording replaced with the 95%
  gate; missing `zenodo-doi-strategy.md` index row added (`793e49b`).
- `docs/guides/styleguide/manuscript-variables.md`: broken `#validationpy`
  anchor repointed to the validation facade in `python_api_manuscript.md` (`793e49b`).
- `manuscript/refs/README.md`: dangling generated-output path clarified to
  post-pipeline existence (`cc4e5fd`).

### Medium (8)

- Root `AGENTS.md`: layout module list omitted `FloatRealResidualWitness`;
  Gate 2 coverage command/note now documents the core-environment gate and the
  documented sim-group exception (`5b50f5c`).
- `CONTRIBUTING.md`: coverage-gate contradiction for sim-enabled setups
  resolved with an explicit note (`5b50f5c`).
- `scripts/README.md`: roster missing `check_concordance.py`,
  `generate_audit_matrix.py`, `gnn_to_pymdp.py`, `simulate_gnn.py`; added with
  docstring-verified descriptions (`7790ac9`).
- `lean/README.md` + `lean/ActinfPolicyEntanglement/AGENTS.md`: 16/17 submodule
  mismatch; added the `FloatRealResidualWitness` index row and map row (`89f5a8b`).
- `docs/guides/quickstart_recipes.md`: 16-module job list, S01–S07 supplement
  count, missing `simulate_gnn.py` in the run_all roster, and template-only
  path assumptions — all corrected; PDF output path aligned to the canonical
  `output/pdf/actinf_policy_entanglement_lean_combined.pdf` (`793e49b`).
- `docs/guides/build_run.md` + `testing.md`: template-monorepo path convention
  now stated with a standalone-clone note (`793e49b`).
- `docs/modules/`: missing page for the 17th Lean module; added
  `float_real_residual_witness.md` (witness structure and theorem quoted from
  source; JSON field mapping verified against `src/manuscript/variables.py`)
  and registered it in `docs/modules/README.md` and `docs/modules/AGENTS.md` (`793e49b`).
- `domain_profile.yaml`: `artifact_expectations` annotated as post-pipeline
  outputs, not checkout invariants (`62cf243`).

### Major (0)

No major documentation-system defect was found. The existing docs index,
guides, module pages, reference pages, API references, and manuscript index
form a coherent system. The only owner-level item noted (not closed): a
separate CC-BY-4.0 license text file for the manuscript prose would require an
ownership decision outside a docs pass; the split is declared consistently in
README, CITATION.cff, and `manuscript/config.yaml`.

## Review coverage note

Two of three parallel review subagents (docs/ tree; code-adjacent docs) hit a
provider billing limit and returned no findings; their scope was covered
in-line instead: mechanical link/anchor/orphan scans over the whole tree,
script-existence verification for every `scripts/*.py` reference, sampled
reads of the workflow guides and subdirectory indexes, and first-hand
verification of every claim edited.

## Verification

- Re-ran the repository hyperlink regression test after edits: passed.
- Re-ran `tests/test_validation_cli_gate.py` (stale-literal scan): 3 passed.
- Parsed `.aii/config.yaml` and `domain_profile.yaml` with PyYAML after edits.
- Confirmed changed references against the filesystem and generated
  declaration counts (17 modules / 76 theorems / 39 defs / 11 structures).
- The full Lean build and pytest suite were not run: this pass changed
  documentation/metadata only; the repo's own gates (hyperlinks, stale
  literals) were run and are green.

## Commits

- `62cf243` fix(metadata): .aii DOI, CITATION.cff version/date, domain_profile annotation
- `5b50f5c` docs(root): README citation/license, AGENTS inventory + coverage gate, CONTRIBUTING note
- `7790ac9` docs(scripts): complete script roster
- `89f5a8b` docs(lean): FloatRealResidualWitness index/map rows
- `793e49b` docs(guides+modules): index gaps, stale counts, broken anchor, new module page
- `cc4e5fd` docs(manuscript): rendered-output wording
