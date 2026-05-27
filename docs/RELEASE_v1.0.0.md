# Release v1.0.0 — Policy Entanglement in Active Inference

Publication surfaces for the public release under
**ActiveInferenceInstitute/policy_entanglement**.

## Canonical identifiers

| Artifact | URL / ID |
| --- | --- |
| GitHub repository | https://github.com/ActiveInferenceInstitute/policy_entanglement |
| Git tag | `v1.0.0` |
| Zenodo concept record | https://zenodo.org/records/20418904 |
| Citation DOI (concept) | https://doi.org/10.5281/zenodo.20418904 |
| Latest version record (v1.0.0) | https://zenodo.org/records/20419637 |
| Latest version DOI | https://doi.org/10.5281/zenodo.20419637 |
| Deposit PDF (v1.0.0) | `Friedman_2026_Policy_ae7cdd62.pdf` (SHA-256 `ae7cdd62…`) |

Release receipt: see `release_bundle/RELEASE_RECEIPT.json` under the template
monorepo copy step when publishing via `scripts/publish_project_release.py`.

## Completed (2026-05-27)

- [x] Flip canonical repository URL across `manuscript/config.yaml`, `CITATION.cff`,
  README/AGENTS hubs, abstract, introduction, and `friedman-2026-actinf-policy-entanglement`
  bibliography entry.
- [x] Mint production Zenodo concept DOI `10.5281/zenodo.20418904` (cite this; resolves to latest version).
- [x] Update `src/manuscript/publication_metadata.py` canon constants and inverted-repo guard.
- [x] Add `manuscript/00_abstract.md` → `0A_abstract.md` symlink for unified release workflow.
- [x] Remove stale “pending DOI / pending archive” prose from §6C.

- [x] Public GitHub repo live at `ActiveInferenceInstitute/policy_entanglement` (org push access confirmed for `docxology`).

## Release execution (2026-05-27)

- [x] Push `main` and annotated tag `v1.0.0` to `ActiveInferenceInstitute/policy_entanglement`.
- [x] Re-render combined PDF with live AII repository URL and citation DOI `10.5281/zenodo.20418904`.
- [x] GitHub release [v1.0.0](https://github.com/ActiveInferenceInstitute/policy_entanglement/releases/tag/v1.0.0) with deposit PDF asset.
- [x] Zenodo version upload (concept record `20418904`; latest version DOI above).

## Citation (preferred)

See [`CITATION.cff`](../CITATION.cff). BibTeX key: `friedman-2026-actinf-policy-entanglement`.
