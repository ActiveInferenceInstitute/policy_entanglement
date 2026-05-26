"""Pipeline, Lean, registry, and toolchain manuscript-variable producers."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from manuscript.registry_facts import registry_structural_facts


def run_all_facts(project_root: Path) -> dict[str, int]:
    run_all_path = project_root / "scripts" / "run_all.py"
    spec = importlib.util.spec_from_file_location("run_all", run_all_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        return {"run_all_script_count": 0}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {"run_all_script_count": int(len(module.SCRIPTS))}


def strip_lean_comments(src: str) -> str:
    out: list[str] = []
    i = 0
    depth = 0
    while i < len(src):
        two = src[i : i + 2]
        if depth == 0 and two == "--":
            while i < len(src) and src[i] != "\n":
                i += 1
            if i < len(src):
                out.append("\n")
                i += 1
            continue
        if two == "/-":
            depth += 1
            i += 2
            continue
        if depth > 0 and two == "-/":
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(src[i])
        elif src[i] == "\n":
            out.append("\n")
        i += 1
    return "".join(out)


def count_lean_declarations(project_root: Path, pattern: str) -> int:
    lean_dir = project_root / "lean" / "ActinfPolicyEntanglement"
    decl_re = re.compile(pattern, re.MULTILINE)
    total = 0
    for path in lean_dir.glob("*.lean"):
        total += len(decl_re.findall(strip_lean_comments(path.read_text(encoding="utf-8"))))
    return total


def lean_facts(project_root: Path) -> dict[str, int]:
    lean_dir = project_root / "lean" / "ActinfPolicyEntanglement"
    lean_submodule_count = len(list(lean_dir.glob("*.lean")))
    lean_def_count = count_lean_declarations(project_root, r"^\s*(?:noncomputable\s+)?def\s+")
    lean_theorem_count = count_lean_declarations(project_root, r"^\s*(?:theorem|lemma)\s+")
    lean_structure_count = count_lean_declarations(project_root, r"^\s*structure\s+")
    lean_scaffolding_theorem_count = 20
    lean_framework_theorem_count = lean_theorem_count - lean_scaffolding_theorem_count
    lean_total_declarations = lean_def_count + lean_theorem_count + lean_structure_count
    return {
        "lean_submodule_count": lean_submodule_count,
        "lean_def_count": lean_def_count,
        "lean_theorem_count": lean_theorem_count,
        "lean_framework_theorem_count": lean_framework_theorem_count,
        "lean_scaffolding_theorem_count": lean_scaffolding_theorem_count,
        "lean_structure_count": lean_structure_count,
        "lean_total_declarations": lean_total_declarations,
        "lean_lake_jobs_total": 22,
    }


def registry_facts(project_root: Path) -> dict[str, int]:
    return registry_structural_facts(project_root)


def toolchain_facts(project_root: Path) -> dict[str, str]:
    toolchain_path = project_root / "lean" / "lean-toolchain"
    lean_toolchain = toolchain_path.read_text(encoding="utf-8").strip() if toolchain_path.exists() else "unknown"
    lean_version = lean_toolchain.rsplit(":", maxsplit=1)[-1] if lean_toolchain else "unknown"
    pymdp_version = "unknown"
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        match = re.search(r'"inferactively-pymdp==([^"]+)"', text)
        if match:
            pymdp_version = match.group(1)
    return {
        "lean_toolchain_pin": lean_toolchain,
        "lean_toolchain_version": lean_version,
        "pymdp_distribution_version": pymdp_version,
    }


__all__ = [
    "count_lean_declarations",
    "lean_facts",
    "registry_facts",
    "run_all_facts",
    "strip_lean_comments",
    "toolchain_facts",
]
