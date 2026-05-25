"""End-to-end veridicality / audit-chain regression suite.

Locks in the contract documented at
``docs/reference/veridical_status.md``: every numeric value in
manuscript prose flows from a real analytical / pymdp computation,
the JSONL run log records sane runtime-bearing pymdp calls, and the
Lean ↔ manuscript ↔ glossary cross-references resolve.

These tests are *integration*: they read the artifacts produced by
``scripts/run_all.py`` (or any subset of the pipeline that has run
recently).  Tests skip cleanly when the relevant artifact is
missing — they are not pre-conditions for development, only for
"the pipeline ran green".
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD

PROJECT = Path(__file__).resolve().parent.parent
MANUSCRIPT = PROJECT / "manuscript"
JSON_PATH = PROJECT / "output" / "data" / "manuscript_variables.json"

CONTROLLED_CATEGORICAL_VARIABLES = {
    "coupling_ablation_kc_matrix",
    "coupling_ablation_variants",
    "coupling_ablation_variants_list",
    "lean_toolchain_pin",
    "lean_toolchain_version",
    "pymdp_distribution_version",
    "pymdp_agent_action_selection",
    "pymdp_agent_inference_algo",
    "robustness_observation_contexts",
    "robustness_interaction_families",
    "robustness_interaction_families_list",
}
LOG_PATH = PROJECT / "output" / "logs" / "pymdp_runs.jsonl"
LEAN_DIR = PROJECT / "lean" / "ActinfPolicyEntanglement"
LABELS = MANUSCRIPT / "refs" / "labels.yaml"
GLOSSARY = MANUSCRIPT / "S06_notation_and_concordance.md"

VAR_RE = re.compile(r"\[\[VAR:([A-Za-z0-9_]+)(?::[^\]]+)?\]\]")


@pytest.fixture(scope="module")
def variables() -> dict:
    if not JSON_PATH.exists():
        # RedTeam Tests H6 (2026-05-20): xfail instead of skip.
        pytest.xfail("manuscript_variables.json not generated yet — run scripts/manuscript_variables.py first")
    return json.loads(JSON_PATH.read_text())


@pytest.fixture(scope="module")
def prose_var_keys() -> set[str]:
    keys: set[str] = set()
    for src in sorted(MANUSCRIPT.glob("*.md")):
        if src.name in MANUSCRIPT_NON_BODY_MD:
            continue
        for m in VAR_RE.finditer(src.read_text()):
            keys.add(m.group(1))
    return keys


# ---------------------------------------------------------------------------
# Audit chain — prose ↔ JSON
# ---------------------------------------------------------------------------


def test_every_prose_var_key_resolves_to_a_value(variables: dict, prose_var_keys: set[str]) -> None:
    """Every `[[VAR:key]]` substituted into manuscript prose must
    appear (as a key) in the variables JSON.
    """
    missing = sorted(prose_var_keys - set(variables.keys()))
    assert not missing, f"prose VARs unresolved in JSON: {missing}"


def test_every_resolved_value_is_real_numeric(variables: dict) -> None:
    """No stub strings.  Every variable is a real `int`, `float`,
    a list of integers, or a sentinel-list string (comma-joined
    floats) whose elements all parse as numbers.

    Sentinel-list strings are an explicit auto-injection convention:
    they let prose splice `λ ∈ {0, 0.5, 1, 2, 4}` without serialising
    the list element-by-element. The values are still numerically
    grounded — every element must parse as a float.
    """
    bad: list[tuple[str, object]] = []
    for k, v in variables.items():
        if k in CONTROLLED_CATEGORICAL_VARIABLES:
            continue
        if isinstance(v, list):
            if not all(isinstance(x, (int, float)) for x in v):
                bad.append((k, v))
        elif isinstance(v, str):
            # Sentinel-list strings: comma-separated numeric tokens.
            tokens = [t.strip() for t in v.split(",") if t.strip()]
            if not tokens:
                bad.append((k, v))
                continue
            for tok in tokens:
                try:
                    float(tok)
                except ValueError:
                    bad.append((k, v))
                    break
        elif not isinstance(v, (int, float)):
            bad.append((k, v))
    assert not bad, f"non-numeric variables: {bad}"


def test_minimum_prose_var_count(prose_var_keys: set[str]) -> None:
    """Sanity: the manuscript should reference at least 30 variables;
    any sudden drop signals an accidental rip-out of the auto-injection
    contract.
    """
    assert len(prose_var_keys) >= 30, (
        f"only {len(prose_var_keys)} prose VARs found — auto-injection contract may have regressed"
    )


def test_pymdp_total_correlation_keys_present(variables: dict) -> None:
    """The pymdp-grounded sentinel-λ TC values must be in the JSON
    (proves the harness ran, not just the closed-form analytics).
    """
    expected = {
        "pymdp_total_correlation_lam_0",
        "pymdp_total_correlation_lam_1",
        "pymdp_total_correlation_lam_2",
        "pymdp_total_correlation_lam_4",
    }
    missing = expected - set(variables.keys())
    assert not missing, f"pymdp TC sentinel-λ keys missing — pymdp may have stubbed: {missing}"
    # λ=0 must be exactly 0 (mean-field baseline witness).
    assert abs(variables["pymdp_total_correlation_lam_0"]) < 1e-12


def test_pymdp_total_correlation_monotone(variables: dict) -> None:
    """TC values at sentinel λ ∈ {0, 1, 2, 4} must be monotone-increasing
    (real coupling effect, not noise).
    """
    seq = [
        variables["pymdp_total_correlation_lam_0"],
        variables["pymdp_total_correlation_lam_1"],
        variables["pymdp_total_correlation_lam_2"],
        variables["pymdp_total_correlation_lam_4"],
    ]
    for i in range(len(seq) - 1):
        assert seq[i + 1] >= seq[i] - 1e-9, f"TC not monotone: {seq}"


# ---------------------------------------------------------------------------
# JSONL run log audit
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def log_records() -> list[dict]:
    if not LOG_PATH.exists():
        # RedTeam Tests H6 (2026-05-20): xfail instead of skip.
        pytest.xfail("pymdp_runs.jsonl not generated yet — run scripts/run_all.py first")
    out = []
    for line in LOG_PATH.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def test_log_records_contain_required_sections(log_records: list[dict]) -> None:
    sections = {r["section"] for r in log_records if "section" in r}
    expected = {
        "figure_pymdp_lambda_sweep",
        "figure_pymdp_rollout",
        "figure_pymdp_free_energies",
    }
    assert expected.issubset(sections), f"run log missing sections: {expected - sections}"


def test_log_records_have_realistic_runtime(log_records: list[dict]) -> None:
    """Real pymdp / JAX inference takes hundreds of ms per λ; a
    sub-millisecond runtime would indicate the call was stubbed.
    Per-section minimums (conservative):

    * `figure_pymdp_lambda_sweep` — at least 50 ms (21 grid points).
    * `figure_pymdp_rollout` — at least 50 ms (10 steps).
    * `figure_pymdp_free_energies` — at least 100 ms (21 bundles).

    The log accumulates across runs; stale records from earlier
    interrupted or stubbed runs are ignored. We take the *most
    recent* record per section (last write wins) so the check
    answers: "was the latest real run timed correctly?"
    """
    floors = {
        "figure_pymdp_lambda_sweep": 50.0,
        "figure_pymdp_rollout": 50.0,
        "figure_pymdp_free_energies": 100.0,
    }
    latest: dict[str, float] = {}
    for r in log_records:
        sec = r.get("section")
        if sec in floors and "runtime_ms" in r:
            latest[sec] = float(r["runtime_ms"])
    for sec, floor in floors.items():
        # Require the section to be present: the `log_records` fixture
        # already xfails when the log is entirely absent, so a log that
        # EXISTS but is missing a required section is a partial/stubbed
        # run and must FAIL — not pass vacuously by skipping the check.
        assert sec in latest, (
            f"{sec} missing from pymdp_runs.jsonl — the most recent run did not log it "
            "(pymdp stubbed or a partial run?)"
        )
        assert latest[sec] >= floor, (
            f"{sec} latest runtime {latest[sec]} ms below floor {floor} ms — "
            "pymdp may have been stubbed in the most recent run"
        )


def test_log_records_are_well_formed(log_records: list[dict]) -> None:
    for r in log_records:
        assert "timestamp" in r
        if "section" in r:
            assert r.get("status") in {"ok", "error"}, r
            assert "runtime_ms" in r


def test_log_records_lambda_zero_baseline(log_records: list[dict]) -> None:
    """Among `figure_pymdp_free_energies` records, the λ = 0 sentinel
    fields must satisfy: coupling_term = 0 and joint_entropy ≈
    marginal_entropy_sum.  This is the mean-field baseline witness.
    """
    fe_records = [r for r in log_records if r.get("section") == "figure_pymdp_free_energies"]
    if not fe_records:
        # RedTeam Tests H6 (2026-05-20): xfail instead of skip.
        pytest.xfail("no free-energies records in log — run scripts/simulate_pymdp.py first")
    # Use the most recent record (last write).
    r = fe_records[-1]
    if "coupling_term_at_lambda_zero" in r:
        assert abs(float(r["coupling_term_at_lambda_zero"])) < 1e-9
    if "joint_entropy_at_lambda_zero" in r and "marginal_entropy_sum_at_lambda_zero" in r:
        gap = abs(float(r["joint_entropy_at_lambda_zero"]) - float(r["marginal_entropy_sum_at_lambda_zero"]))
        assert gap < 1e-9


# ---------------------------------------------------------------------------
# Lean ↔ manuscript audit
# ---------------------------------------------------------------------------


def test_every_registered_lean_companion_resolves() -> None:
    """Every theorem in `manuscript/refs/labels.yaml` with both
    `lean_module` and `lean_name` must point to an actual Lean
    source location reachable by the snippet extractor.
    """
    import sys

    sys.path.insert(0, str(PROJECT / "src" / "manuscript"))
    from manuscript.lean_extract import load_lean_snippets
    from manuscript.registry import load_registry

    reg = load_registry(MANUSCRIPT / "refs")
    snippets = load_lean_snippets(LEAN_DIR)
    missing: list[str] = []
    for label, t in reg.labels.theorems.items():
        if not (t.lean_module and t.lean_name):
            continue
        if (t.lean_module, t.lean_name) not in snippets:
            missing.append(f"{label}: {t.lean_module}.{t.lean_name}")
    assert not missing, f"theorem-Lean companions missing: {missing}"


def test_lean_boundary_is_strict_sorry_free() -> None:
    """The boundary fragment must contain zero strict `sorry` — no
    bare `sorry`, no `:= sorry`, no `by sorry`.  Lexical mentions
    inside `/-! ... -/` docstrings are allowed (and intentional).
    """
    strict_sorry = re.compile(r"^[\s]*sorry\b|:=\s*sorry\b|by[\s]+sorry\b")
    offenses: list[str] = []
    for p in sorted(LEAN_DIR.glob("*.lean")):
        for n, line in enumerate(p.read_text().splitlines(), start=1):
            # Ignore obvious docstring lines.
            stripped = line.strip()
            if stripped.startswith("/-") or stripped.startswith("--"):
                continue
            if "`sorry`" in line:  # mention inside backticks
                continue
            if strict_sorry.search(line):
                offenses.append(f"{p.name}:{n}: {stripped}")
    assert not offenses, f"strict `sorry` regression: {offenses}"


# ---------------------------------------------------------------------------
# Glossary ↔ source coherence
# ---------------------------------------------------------------------------


def test_glossary_lean_abbreviations_resolve_in_source() -> None:
    """Every Lean abbreviation listed in §2a's "Lean type abbrevs"
    table must appear in at least one boundary submodule's source.
    """
    glossary = GLOSSARY.read_text()
    table_section_re = re.compile(
        r"## Lean type abbreviations\s*\n\n.*?(?=\n## )",
        re.DOTALL,
    )
    m = table_section_re.search(glossary)
    assert m, "glossary missing Lean abbrev table"
    table = m.group(0)
    abbrev_re = re.compile(r"`([A-Z][A-Za-z]+(?: \w+)?)`", re.MULTILINE)
    abbrevs = {
        a
        for a in abbrev_re.findall(table)
        if " " not in a and a not in {"Nat", "Float", "Type", "Bool", "Fin", "Mathlib", "Lean"}
    }
    if not abbrevs:
        pytest.skip("no Lean abbrevs identified in glossary table")
    src = "\n".join(p.read_text() for p in LEAN_DIR.glob("*.lean"))
    missing = [a for a in abbrevs if a not in src]
    assert not missing, f"glossary lists Lean abbrevs not present in boundary source: {missing}"
