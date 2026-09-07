"""Project-local combined-PDF renderer (library implementation)."""

from __future__ import annotations

import re
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from manuscript.bibliography import write_references_bib
from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD
from manuscript.registry import load_registry
from manuscript.renderer import render_all
from manuscript.variables import write_manuscript_variables
from orchestration.pdf_compile import (
    COMBINED_STEM,
    latex_to_pdf,
    pandoc_to_tex,
)
from orchestration.pdf_config import ManuscriptConfig
from orchestration.pdf_tex_patch import patch_red_hyperlinks, postprocess_combined_tex

# Backward-compatible aliases for tests.
_patch_red_hyperlinks = patch_red_hyperlinks


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_sequence(value: object) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()


def _load_config(source_manuscript: Path) -> dict[str, Any]:
    return dict(ManuscriptConfig.load(source_manuscript).raw)


def _metadata_args(config: object, *, project_root: Path) -> list[str]:
    raw = config if isinstance(config, dict) else {}
    return ManuscriptConfig(raw=raw).pandoc_metadata_args(project_root=project_root)


def _author_block_from_config(config: object) -> str:
    raw = config if isinstance(config, dict) else {}
    return ManuscriptConfig(raw=raw).author_block()


def _postprocess_combined_tex(*, combined_tex: Path, source_manuscript: Path) -> None:
    postprocess_combined_tex(
        combined_tex=combined_tex,
        config=ManuscriptConfig.load(source_manuscript),
    )


def _section_sort_key(path: Path) -> tuple[int, str]:
    return (1, path.name) if path.name == "99_bibliography.md" else (0, path.name)


def _discover_manuscript_files(injected_manuscript: Path) -> list[Path]:
    files = [path for path in injected_manuscript.glob("*.md") if path.name not in MANUSCRIPT_NON_BODY_MD]
    return sorted(files, key=_section_sort_key)


def _mirror_render_auxiliary_files(*, source_manuscript: Path, injected_manuscript: Path) -> None:
    if not source_manuscript.is_dir() or not injected_manuscript.is_dir():
        return
    for name in ("config.yaml", "preamble.md"):
        src = source_manuscript / name
        dst = injected_manuscript / name
        if src.is_file():
            shutil.copy2(src, dst)
    for bib in sorted(source_manuscript.glob("*.bib")):
        shutil.copy2(bib, injected_manuscript / bib.name)


def _normalise_render_paths(text: str) -> str:
    return text.replace("](../output/figures/", "](../figures/")


def _write_combined_markdown(source_files: Sequence[Path], *, combined_md: Path) -> None:
    combined_md.parent.mkdir(parents=True, exist_ok=True)
    blocks = [_normalise_render_paths(path.read_text(encoding="utf-8")).rstrip() for path in source_files]
    combined_md.write_text("\n\n---\n\n".join(blocks) + "\n", encoding="utf-8")


def _clean_combined_artifacts(*, pdf_dir: Path, pdf_path: Path, preamble_tex: Path, xelatex_stdout: Path) -> None:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for path in pdf_dir.glob(f"{COMBINED_STEM}.*"):
        if path.is_file():
            path.unlink()
    for path in (pdf_path, preamble_tex, xelatex_stdout):
        if path.is_file():
            path.unlink()


def _extract_latex_preamble(markdown: str) -> str:
    match = re.search(r"```latex\n(?P<body>.*?)```", markdown, flags=re.DOTALL)
    if match:
        return match.group("body").strip() + "\n"
    return markdown.strip() + "\n"


def _write_preamble_tex(*, source_manuscript: Path, preamble_tex: Path) -> None:
    preamble_tex.write_text(
        _extract_latex_preamble((source_manuscript / "preamble.md").read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def inject_rendered_manuscript(*, project_root: Path) -> int:
    """Compute variables and render injected manuscript sections via library APIs."""
    manuscript_dir = project_root / "docs" / "manuscript"
    if not (manuscript_dir / "refs" / "labels.yaml").exists():
        print(
            "FAILED: docs/manuscript/refs/labels.yaml not found — run from a "
            "project checkout that contains the manuscript registry",
            file=sys.stderr,
        )
        return 1
    write_manuscript_variables(project_root=project_root)
    refs_dir = manuscript_dir / "refs"
    registry = load_registry(refs_dir)
    output_dir = project_root / "output" / "manuscript"
    variables_path = project_root / "output" / "data" / "manuscript_variables.json"
    lean_dir = project_root / "lean" / "ActinfPolicyEntanglement"
    results = render_all(
        manuscript_dir=manuscript_dir,
        output_dir=output_dir,
        registry=registry,
        variables_path=variables_path,
        lean_dir=lean_dir,
    )
    incomplete = [name for name, result in results.items() if not result.is_complete]
    output_dir.mkdir(parents=True, exist_ok=True)
    for support in ("config.yaml", "preamble.md"):
        src = manuscript_dir / support
        if src.exists():
            shutil.copy2(src, output_dir / support)
    for bib in manuscript_dir.glob("*.bib"):
        shutil.copy2(bib, output_dir / bib.name)
    write_references_bib(registry.citations, output_dir / "references.bib")
    if incomplete:
        print(
            f"FAILED: {len(incomplete)} section(s) had unresolved tokens",
            file=sys.stderr,
        )
        return 1
    return 0


def regenerate_injected_manuscript(*, project_root: Path) -> int:
    return inject_rendered_manuscript(project_root=project_root)


def render_combined_pdf(*, project_root: Path) -> Path:
    pdf_dir = project_root / "output" / "pdf"
    pdf_path = pdf_dir / "actinf_policy_entanglement_lean_combined.pdf"
    combined_md = pdf_dir / f"{COMBINED_STEM}.md"
    combined_tex = pdf_dir / f"{COMBINED_STEM}.tex"
    preamble_tex = pdf_dir / "_preamble.tex"
    xelatex_stdout = pdf_dir / "_xelatex_stdout.log"
    injected_manuscript = project_root / "output" / "manuscript"
    source_manuscript = project_root / "docs" / "manuscript"
    config = ManuscriptConfig.load(source_manuscript)

    _mirror_render_auxiliary_files(
        source_manuscript=source_manuscript,
        injected_manuscript=injected_manuscript,
    )
    source_files = _discover_manuscript_files(injected_manuscript)
    if not source_files:
        raise FileNotFoundError(f"no injected manuscript markdown files found in {injected_manuscript}")
    _clean_combined_artifacts(
        pdf_dir=pdf_dir,
        pdf_path=pdf_path,
        preamble_tex=preamble_tex,
        xelatex_stdout=xelatex_stdout,
    )
    references = injected_manuscript / "references.bib"
    if references.exists():
        shutil.copy2(references, pdf_dir / "references.bib")

    _write_combined_markdown(source_files, combined_md=combined_md)
    _write_preamble_tex(source_manuscript=source_manuscript, preamble_tex=preamble_tex)
    pandoc_to_tex(
        combined_md=combined_md,
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        preamble_tex=preamble_tex,
        config=config,
        project_root=project_root,
    )
    return latex_to_pdf(
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        pdf_path=pdf_path,
        xelatex_stdout=xelatex_stdout,
    )


def main(*, project_root: Path) -> int:
    code = regenerate_injected_manuscript(project_root=project_root)
    if code != 0:
        return code
    pdf_path = project_root / "output" / "pdf" / "actinf_policy_entanglement_lean_combined.pdf"
    try:
        produced = render_combined_pdf(project_root=project_root)
    except Exception as exc:  # noqa: BLE001 - CLI wrapper reports the concrete renderer failure.
        print(f"!!! combined PDF render failed: {exc}", file=sys.stderr)
        return 1
    if not pdf_path.exists():
        print(f"!!! expected PDF was not created: {pdf_path}", file=sys.stderr)
        return 1
    if produced.resolve() != pdf_path.resolve():
        print(f"!!! renderer returned unexpected PDF path: {produced}", file=sys.stderr)
        return 1
    print(pdf_path.relative_to(project_root))
    return 0


__all__ = [
    "COMBINED_STEM",
    "_author_block_from_config",
    "_discover_manuscript_files",
    "_patch_red_hyperlinks",
    "_postprocess_combined_tex",
    "inject_rendered_manuscript",
    "main",
    "regenerate_injected_manuscript",
    "render_combined_pdf",
]
