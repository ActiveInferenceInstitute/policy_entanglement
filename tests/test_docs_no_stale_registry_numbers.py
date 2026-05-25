"""Repo-wide docs gate for present-tense registry-mirroring counts.

This test scans current-facing docs and manuscript sources for live-count
assertions that mirror generated registry and build totals, and fails when a present-tense
assertion has drifted from the current oracle. It intentionally does
not flag:

* historical or dated context such as ``Round 3``, ``per-round``,
  ``revision history``, ``changelog``, ``as of 2026-05-12``,
  ``last updated``, or delta phrasing such as ``57 -> 75`` and
  ``(+6)``;
* per-Lean-module inventory lines like
  ``FreeEnergy.lean (9 defs, 3 theorems)`` because those are local
  module counts, not repo-wide registry totals;
* ``docs/CHANGELOG.md`` entirely, because that file is historical by
  definition.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT = Path(__file__).resolve().parent.parent
MANUSCRIPT_VARIABLES_JSON = PROJECT / "output" / "data" / "manuscript_variables.json"
MANUSCRIPT_VARIABLES_SCRIPT = PROJECT / "scripts" / "manuscript_variables.py"
RUN_ALL_SCRIPT = PROJECT / "scripts" / "run_all.py"
LABELS_YAML = PROJECT / "manuscript" / "refs" / "labels.yaml"
CITATIONS_YAML = PROJECT / "manuscript" / "refs" / "citations.yaml"
DOCS_DIR = PROJECT / "docs"
CHANGELOG_RELATIVE = Path("docs/CHANGELOG.md")
AUDIT_RELATIVE = Path("docs/_audit")

COUNT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)Build completed successfully\s*\(\s*(\d+)\s+jobs?\s*\)"),
        "lean_lake_jobs_total",
    ),
    (
        re.compile(r"(?i)\bmanuscript_section_file_count\b.*?\bcurrent value:\s*\*\*(\d+)\*\*"),
        "manuscript_section_file_count",
    ),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+total declarations\b"), "lean_total_declarations"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+declarations\b"), "lean_total_declarations"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+public theorems\s*/\s*lemmas\b"), "lean_theorem_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+public theorems\b"), "lean_theorem_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+theorems\s*/\s*lemmas\b"), "lean_theorem_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+defs\b"), "lean_def_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+`def`s\b"), "lean_def_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+structures\b"), "lean_structure_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+witness `structure`s\b"), "lean_structure_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+figures\b"), "labels_figures_len"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+total figure registry entries\b"), "labels_figures_len"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+registered equations\b"), "labels_equations_len"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+YAML entries\b"), "citations_yaml_keys"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+YAML keys\b"), "citations_yaml_keys"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+actual citations\b"), "citations_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+citations\b"), "citations_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+analysis scripts\b"), "run_all_scripts_len"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+scripts\b"), "run_all_scripts_len"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)(?:st|nd|rd|th)?[`*]*\s+lake jobs?\b"), "lean_lake_jobs_total"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)(?:st|nd|rd|th)?[`*]*\s+`?lake`?\s+jobs?\b"), "lean_lake_jobs_total"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s*/\s*[`*]*\d+[`*]*\s+(?:`?lake`?\s+)?jobs?\b"), "lean_lake_jobs_total"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+Lean submodules\b"), "lean_submodule_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+submodules\b"), "lean_submodule_count"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+proved\b(?!\s+\w)"), "tally_proved"),
    (re.compile(r"(?i)(?:^|[^\w])[`*]*(\d+)[`*]*\s+witness\b(?!\s+(?:`|\w))"), "tally_witness"),
]

HISTORICAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\bround-\d+\b"),
    re.compile(r"(?i)\bround \d+\b"),
    re.compile(r"(?i)\bas of round\b"),
    re.compile(r"(?i)\bper-round\b"),
    re.compile(r"(?i)\brevision history\b"),
    re.compile(r"(?i)\bchangelog\b"),
    re.compile(r"(?i)\bas of \d"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"(?i)\blast reviewed\b"),
    re.compile(r"(?i)\blast updated\b"),
    re.compile(r"(?i)\bwas \d+\b"),
    re.compile(r"(?i)\badds? \d+\b"),
    re.compile(r"(?i)\bproduces \d+ extra\b"),
    re.compile(r"(?i)\bhardcoded\b"),
    re.compile(r"(?i)\blegacy key\b"),
    re.compile(r"\d+\s*(?:→|->)\s*\d+"),
    re.compile(r"\(\+\d+"),
)

LEAN_TOKEN_RE = re.compile(r"`?[\w./-]+\.lean`?")
PARENTHESIZED_NUMBER_RE = re.compile(r"\([^)]*\d+[^)]*\)")
CURRENT_COUNT_CONTEXT_RE = re.compile(
    r"(?i)Build completed successfully|boundary submodules|manuscript_section_file_count"
)


def _load_module(module_name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _oracle() -> dict[str, int]:
    variables: dict[str, int] | None = None
    if MANUSCRIPT_VARIABLES_JSON.is_file():
        payload = json.loads(MANUSCRIPT_VARIABLES_JSON.read_text(encoding="utf-8"))
        raw_variables = payload.get("variables") if isinstance(payload, dict) else None
        if isinstance(raw_variables, dict):
            variables = {key: int(value) for key, value in raw_variables.items() if isinstance(value, int)}
        elif isinstance(payload, dict):
            variables = {key: int(value) for key, value in payload.items() if isinstance(value, int)}
    elif MANUSCRIPT_VARIABLES_SCRIPT.is_file():
        module = _load_module("manuscript_variables", MANUSCRIPT_VARIABLES_SCRIPT)
        try:
            lean_facts = module._lean_facts(PROJECT)
            registry_facts = module._registry_facts(PROJECT)
            run_all_facts = module._run_all_facts(PROJECT)
        except Exception:  # pragma: no cover - defensive skip path
            pytest.skip(
                "output/data/manuscript_variables.json missing; run `uv run python scripts/manuscript_variables.py` first"
            )
        variables = {
            "lean_theorem_count": int(lean_facts["lean_theorem_count"]),
            "lean_def_count": int(lean_facts["lean_def_count"]),
            "lean_structure_count": int(lean_facts["lean_structure_count"]),
            "lean_total_declarations": int(lean_facts["lean_total_declarations"]),
            "lean_submodule_count": int(lean_facts["lean_submodule_count"]),
            "lean_lake_jobs_total": int(lean_facts["lean_lake_jobs_total"]),
            "run_all_script_count": int(run_all_facts["run_all_script_count"]),
            "manuscript_section_file_count": int(registry_facts["manuscript_section_file_count"]),
        }
    else:
        pytest.skip(
            "output/data/manuscript_variables.json missing; run `uv run python scripts/manuscript_variables.py` first"
        )

    labels = yaml.safe_load(LABELS_YAML.read_text(encoding="utf-8"))
    citations = yaml.safe_load(CITATIONS_YAML.read_text(encoding="utf-8"))
    run_all = _load_module("run_all", RUN_ALL_SCRIPT)

    theorems = labels["theorems"]
    status_tally: dict[str, int] = {
        "proved": 0,
        "witness": 0,
        "boundary": 0,
        "forwarder": 0,
        "roadmap": 0,
        "deferred": 0,
        "sketch": 0,
    }
    for entry in theorems.values():
        status_tally[str(entry["status"])] += 1

    ignored_citation_keys = {"topic_order", "topic_titles"}
    citations_yaml_keys = len(citations)
    citations_count = citations_yaml_keys - len(ignored_citation_keys & set(citations))
    run_all_scripts_len = len(run_all.SCRIPTS)
    if "run_all_script_count" in variables:
        assert run_all_scripts_len == variables["run_all_script_count"]

    return {
        "lean_theorem_count": variables["lean_theorem_count"],
        "lean_def_count": variables["lean_def_count"],
        "lean_structure_count": variables["lean_structure_count"],
        "lean_total_declarations": variables["lean_total_declarations"],
        "lean_submodule_count": variables["lean_submodule_count"],
        "lean_lake_jobs_total": variables["lean_lake_jobs_total"],
        "manuscript_section_file_count": variables["manuscript_section_file_count"],
        "labels_figures_len": len(labels["figures"]),
        "labels_equations_len": len(labels["equations"]),
        "labels_theorems_len": len(theorems),
        "citations_yaml_keys": citations_yaml_keys,
        "citations_count": citations_count,
        "run_all_scripts_len": run_all_scripts_len,
        "tally_proved": status_tally["proved"],
        "tally_witness": status_tally["witness"],
    }


def _is_excluded_history_path(rel_path: Path) -> bool:
    return rel_path in (CHANGELOG_RELATIVE, AUDIT_RELATIVE) or AUDIT_RELATIVE in rel_path.parents


def _is_per_module_local_count(line: str) -> bool:
    """Skip local ``Module.lean (9 defs, 3 theorems)`` inventory lines."""
    return bool(LEAN_TOKEN_RE.search(line) and PARENTHESIZED_NUMBER_RE.search(line))


def _is_historical_context(line: str, heading: str) -> bool:
    if CURRENT_COUNT_CONTEXT_RE.search(line):
        return False
    text = f"{heading}\n{line}"
    return any(pattern.search(text) for pattern in HISTORICAL_PATTERNS)


def _violations_in_line(line: str, heading: str, oracle: dict[str, int]) -> list[tuple[int, str, int]]:
    if _is_historical_context(line, heading):
        return []
    if _is_per_module_local_count(line):
        return []

    violations: list[tuple[int, str, int]] = []
    for pattern, oracle_key in COUNT_PATTERNS:
        for match in pattern.finditer(line):
            asserted = int(match.group(1))
            expected = oracle[oracle_key]
            if asserted != expected:
                violations.append((asserted, oracle_key, expected))
    return violations


def _scan_doc_assertions(project: Path) -> list[tuple[str, int, int, str, int]]:
    oracle = _oracle()
    violations: list[tuple[str, int, int, str, int]] = []
    candidates = [
        project / "README.md",
        project / "AGENTS.md",
        *sorted((project / "docs").rglob("*.md")),
        *sorted((project / "manuscript").rglob("*.md")),
    ]
    for path in candidates:
        if not path.exists():
            continue
        rel_path = path.relative_to(project)
        if _is_excluded_history_path(rel_path):
            continue
        heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                heading = stripped
            for asserted, oracle_key, expected in _violations_in_line(line, heading, oracle):
                violations.append((str(rel_path), lineno, asserted, oracle_key, expected))
    return violations


def test_docs_have_no_stale_registry_numbers() -> None:
    violations = _scan_doc_assertions(PROJECT)
    assert not violations, "\n".join(
        f"{rel}:{lineno}: asserts {asserted} but {oracle_key} oracle = {expected}"
        for rel, lineno, asserted, oracle_key, expected in violations
    )


def test_history_predicate_excludes_synthetic_historical() -> None:
    assert _is_historical_context("Round 3: 57 theorems", "")
    assert _is_historical_context("57 → 75 theorems", "")
    assert _is_excluded_history_path(Path("docs/CHANGELOG.md"))


def test_scanner_catches_synthetic_present_tense() -> None:
    fake_oracle = {
        "lean_total_declarations": 126,
        "lean_theorem_count": 76,
        "lean_def_count": 39,
        "lean_structure_count": 11,
        "labels_theorems_len": 20,
        "labels_figures_len": 44,
        "labels_equations_len": 11,
        "citations_yaml_keys": 82,
        "citations_count": 80,
        "run_all_scripts_len": 17,
        "lean_lake_jobs_total": 21,
        "lean_submodule_count": 17,
        "manuscript_section_file_count": 38,
        "tally_proved": 5,
        "tally_witness": 11,
    }

    violations = _violations_in_line("The fragment exposes 999 total declarations.", "", fake_oracle)

    assert violations == [(999, "lean_total_declarations", 126)]
    lake_violations = _violations_in_line(
        "Expected output: `Build completed successfully (20 jobs).`",
        "",
        fake_oracle,
    )
    assert lake_violations == [(20, "lean_lake_jobs_total", 21)]
    section_violations = _violations_in_line(
        "| `manuscript_section_file_count` | current value: **37** |",
        "",
        fake_oracle,
    )
    assert section_violations == [(37, "manuscript_section_file_count", 38)]


def test_per_module_carveout_skips_module_inventory() -> None:
    fake_oracle = {
        "lean_total_declarations": 126,
        "lean_theorem_count": 76,
        "lean_def_count": 39,
        "lean_structure_count": 11,
        "labels_theorems_len": 20,
        "labels_figures_len": 44,
        "labels_equations_len": 11,
        "citations_yaml_keys": 82,
        "citations_count": 80,
        "run_all_scripts_len": 17,
        "lean_lake_jobs_total": 21,
        "lean_submodule_count": 17,
        "manuscript_section_file_count": 38,
        "tally_proved": 5,
        "tally_witness": 11,
    }

    line = "| Lean module | `FreeEnergy.lean` (9 defs, 3 theorems). |"
    assert _violations_in_line(line, "", fake_oracle) == []
