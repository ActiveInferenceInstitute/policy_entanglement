"""Cross-reference registry integrity tests.

Every entry in :data:`simulation.cross_references.CROSS_REFERENCES`
points at one or more of:

* a manuscript label (`theorem`, `equation`, `section`),
* a Lean declaration in `lean/ActinfPolicyEntanglement/`,
* a MathlibProofs declaration in `lean/MathlibProofs/MathlibProofs.lean`,
* a Python function `simulation.module.function`.

This test gate pins each of those resolutions so a future rename anywhere
in the codebase or manuscript surfaces here, not at render time.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parent.parent
_SRC = str(PROJECT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from simulation.cross_references import (  # noqa: E402
    CROSS_REFERENCES,
    CrossReference,
    as_metadata_dict,
    cross_reference_for,
    to_markdown_table,
)

LABELS_PATH = PROJECT / "manuscript" / "refs" / "labels.yaml"
LEAN_DIR = PROJECT / "lean" / "ActinfPolicyEntanglement"
MATHLIB_PROOFS = PROJECT / "lean" / "MathlibProofs" / "MathlibProofs.lean"


def _entries_with(field_name: str) -> tuple[CrossReference, ...]:
    return tuple(entry for entry in CROSS_REFERENCES if getattr(entry, field_name) is not None)


def _functions_without(field_name: str) -> set[str]:
    return {entry.function for entry in CROSS_REFERENCES if getattr(entry, field_name) is None}


THEOREM_REFERENCES = _entries_with("theorem")
EQUATION_REFERENCES = _entries_with("equation")
LEAN_REFERENCES = _entries_with("lean_declaration")
MATHLIB_REFERENCES = _entries_with("mathlib_proof")

EXPECTED_NO_THEOREM = {
    "simulation.btai_baseline.run_btai_scenario",
    "simulation.adversarial.measure_drift",
}
EXPECTED_NO_EQUATION = {
    "simulation.rollout.simulate_coupled_rollout",
    "simulation.long_horizon.long_horizon_rollout",
    "simulation.multi_k_experiments.run_multi_k_sweep",
    "simulation.btai_baseline.run_btai_scenario",
}
EXPECTED_NO_LEAN = {
    "simulation.btai_baseline.run_btai_scenario",
    "simulation.adversarial.measure_drift",
}
EXPECTED_NO_MATHLIB = {
    "simulation.rollout.simulate_coupled_rollout",
    "simulation.long_horizon.long_horizon_rollout",
    "simulation.multi_k_experiments.run_multi_k_sweep",
    "simulation.btai_baseline.run_btai_scenario",
    "simulation.adversarial.measure_drift",
}


def _labels() -> dict:
    return yaml.safe_load(LABELS_PATH.read_text(encoding="utf-8")) or {}


def test_cross_references_non_empty() -> None:
    """The registry pins at least the headline witnesses."""
    assert len(CROSS_REFERENCES) >= 8


def test_optional_blank_cross_reference_fields_are_intentional() -> None:
    """Optional registry blanks are pinned explicitly instead of skipped."""
    assert _functions_without("theorem") == EXPECTED_NO_THEOREM
    assert _functions_without("equation") == EXPECTED_NO_EQUATION
    assert _functions_without("lean_declaration") == EXPECTED_NO_LEAN
    assert _functions_without("mathlib_proof") == EXPECTED_NO_MATHLIB


@pytest.mark.parametrize("entry", THEOREM_REFERENCES, ids=lambda e: e.function)
def test_every_theorem_resolves_in_labels(entry: CrossReference) -> None:
    """Every registered `theorem` is a real registry key."""
    theorems = _labels().get("theorems", {})
    assert entry.theorem in theorems, (
        f"{entry.function}: theorem '{entry.theorem}' missing from "
        f"manuscript/refs/labels.yaml::theorems — rename or add the key"
    )


@pytest.mark.parametrize("entry", EQUATION_REFERENCES, ids=lambda e: e.function)
def test_every_equation_resolves_in_labels(entry: CrossReference) -> None:
    """Every registered `equation` is a real registry key."""
    equations = _labels().get("equations", {})
    assert entry.equation in equations, (
        f"{entry.function}: equation '{entry.equation}' missing from manuscript/refs/labels.yaml::equations"
    )


@pytest.mark.parametrize("entry", CROSS_REFERENCES, ids=lambda e: e.function)
def test_every_section_resolves_in_labels(entry: CrossReference) -> None:
    """Every registered `section` is a real registry key."""
    sections = _labels().get("sections", {})
    assert entry.section in sections, (
        f"{entry.function}: section '{entry.section}' missing from manuscript/refs/labels.yaml::sections"
    )


@pytest.mark.parametrize("entry", LEAN_REFERENCES, ids=lambda e: e.function)
def test_every_lean_declaration_resolves(entry: CrossReference) -> None:
    """Every registered Lean declaration exists in the boundary fragment."""
    # Lean declaration format is "Module.name" or "Module.Sub.name" etc.
    parts = entry.lean_declaration.split(".")
    decl_name = parts[-1]
    # The Lean module is the first component (the boundary fragment is a
    # single Lean namespace per module; nested namespaces are visited
    # textually via grep).
    assert LEAN_DIR.exists(), "Lean source tree not present"
    declared_in = []
    for lean_file in LEAN_DIR.glob("*.lean"):
        text = lean_file.read_text(encoding="utf-8")
        # Match `theorem`/`lemma`/`def` followed by the name (allowing
        # for binders like `{α} [CommScalar α]` between).
        if re.search(rf"\b(theorem|lemma|def|abbrev)\s+{re.escape(decl_name)}\b", text):
            declared_in.append(lean_file.name)
    assert declared_in, (
        f"{entry.function}: Lean declaration '{entry.lean_declaration}' "
        f"not found in lean/ActinfPolicyEntanglement/*.lean"
    )


@pytest.mark.parametrize("entry", MATHLIB_REFERENCES, ids=lambda e: e.function)
def test_every_mathlib_proof_resolves(entry: CrossReference) -> None:
    """Every registered MathlibProofs declaration exists."""
    assert MATHLIB_PROOFS.exists(), "MathlibProofs source not present"
    text = MATHLIB_PROOFS.read_text(encoding="utf-8")
    assert re.search(rf"\b(theorem|lemma|def)\s+{re.escape(entry.mathlib_proof)}\b", text), (
        f"{entry.function}: MathlibProofs declaration '{entry.mathlib_proof}' not found in MathlibProofs.lean"
    )


@pytest.mark.parametrize("entry", CROSS_REFERENCES, ids=lambda e: e.function)
def test_every_function_qualifier_imports(entry: CrossReference) -> None:
    """Every registered Python function qualifier actually imports."""
    parts = entry.function.split(".")
    module_path = ".".join(parts[:-1])
    func_name = parts[-1]
    module = importlib.import_module(module_path)
    assert hasattr(module, func_name), (
        f"cross-reference {entry.function!r} does not resolve: {module_path} has no attribute {func_name!r}"
    )


def test_cross_reference_for_known_function() -> None:
    """The lookup helper finds a known entry."""
    entry = cross_reference_for("simulation.inference.coupled_policy_posterior")
    assert entry is not None
    assert entry.theorem == "thm_4_1"


def test_cross_reference_for_unknown_returns_none() -> None:
    """The lookup helper returns None for an unknown qualifier."""
    assert cross_reference_for("simulation.does_not_exist") is None


def test_as_metadata_dict_uses_source_tokens() -> None:
    """The metadata renderer emits source-format manuscript tokens."""
    entry = cross_reference_for("simulation.inference.coupled_policy_posterior")
    assert entry is not None
    md = as_metadata_dict(entry)
    assert md["project.cross_reference.theorem"] == "[[THMREF:thm_4_1]]"
    assert md["project.cross_reference.equation"] == "[[EQREF:tc_decomp]]"
    assert md["project.cross_reference.section"] == "[[SECREF:decomposition]]"
    assert md["project.cross_reference.lean_declaration"].startswith("Decomposition.")
    assert md["project.cross_reference.mathlib_proof"].startswith("MathlibProofs.")


def test_markdown_table_renders() -> None:
    """The markdown-table renderer emits a valid header + per-row table."""
    table = to_markdown_table()
    lines = table.splitlines()
    assert lines[0].startswith("| Function")
    assert lines[1].startswith("|---")
    # One row per registered cross-reference.
    assert len(lines) == 2 + len(CROSS_REFERENCES)


def test_no_duplicate_function_qualifiers() -> None:
    """Each function appears at most once in the registry."""
    qualifiers = [entry.function for entry in CROSS_REFERENCES]
    duplicates = {q for q in qualifiers if qualifiers.count(q) > 1}
    assert not duplicates, f"duplicate cross-reference function names: {duplicates}"
