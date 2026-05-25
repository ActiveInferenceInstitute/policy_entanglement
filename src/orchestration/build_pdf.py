"""Project-local combined-PDF renderer (library implementation).

Business logic for :doc:`scripts/build_pdf.py </scripts/build_pdf>`. This
checkout is standalone; the renderer regenerates the injected manuscript
tree, combines the rendered Markdown sections, converts the bundle to TeX
with Pandoc, and runs the local XeLaTeX/BibTeX pass that
:doc:`scripts/validate_pdf.py </scripts/validate_pdf>` audits.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from manuscript.meta_files import MANUSCRIPT_NON_BODY_MD

COMBINED_STEM = "_combined_manuscript"


def _run_project_script(script_name: str, *, project_root: Path) -> int:
    script = project_root / "scripts" / script_name
    proc = subprocess.run([sys.executable, str(script)], cwd=str(project_root), check=False)
    return proc.returncode


def regenerate_injected_manuscript(*, project_root: Path) -> int:
    """Run the variable-build + token-injection scripts in order."""
    for script_name in ("manuscript_variables.py", "inject_manuscript_variables.py"):
        code = _run_project_script(script_name, project_root=project_root)
        if code != 0:
            print(f"!!! {script_name} failed with exit code {code}", file=sys.stderr)
            return code
    return 0


def _mirror_render_auxiliary_files(*, source_manuscript: Path, injected_manuscript: Path) -> None:
    """Copy rendering-critical config/bibliography files into the injected tree."""
    if not source_manuscript.is_dir() or not injected_manuscript.is_dir():
        return
    for name in ("config.yaml", "preamble.md"):
        src = source_manuscript / name
        dst = injected_manuscript / name
        if src.is_file():
            shutil.copy2(src, dst)
    for bib in sorted(source_manuscript.glob("*.bib")):
        shutil.copy2(bib, injected_manuscript / bib.name)


def _section_sort_key(path: Path) -> tuple[int, str]:
    """Keep bibliography last, after the supplements."""
    return (1, path.name) if path.name == "99_bibliography.md" else (0, path.name)


def _discover_manuscript_files(injected_manuscript: Path) -> list[Path]:
    files = [path for path in injected_manuscript.glob("*.md") if path.name not in MANUSCRIPT_NON_BODY_MD]
    return sorted(files, key=_section_sort_key)


def _normalise_render_paths(text: str) -> str:
    """Make rendered links/image paths resolve from ``output/pdf``."""
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


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_sequence(value: object) -> Sequence[object]:
    return value if isinstance(value, Sequence) and not isinstance(value, str) else ()


def _load_config(source_manuscript: Path) -> Mapping[str, Any]:
    config_path = source_manuscript / "config.yaml"
    if not config_path.exists():
        return {}
    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return _as_mapping(loaded)


def _metadata_args(*, source_manuscript: Path, project_root: Path) -> list[str]:
    config = _load_config(source_manuscript)
    paper = _as_mapping(config.get("paper"))
    authors = _as_sequence(config.get("authors"))
    first_author = _as_mapping(authors[0]) if authors else {}

    title = str(paper.get("title") or project_root.name)
    subtitle = str(paper.get("subtitle") or "")
    date = str(paper.get("date") or "")
    author_name = str(first_author.get("name") or "")

    metadata = [
        "title=" + (f"{title}\\\\\\normalsize {subtitle}" if subtitle else title),
        f"date={date}",
    ]
    if author_name:
        metadata.append(f"author={author_name}")
    args: list[str] = []
    for item in metadata:
        args.extend(["--metadata", item])
    return args


def _run(cmd: Sequence[str], *, cwd: Path, stdout_path: Path | None = None) -> None:
    proc = subprocess.run(
        list(cmd),
        cwd=str(cwd),
        capture_output=True,
        check=False,
        text=True,
    )
    output = proc.stdout + proc.stderr
    if stdout_path is not None:
        stdout_path.write_text(output, encoding="utf-8")
    if proc.returncode != 0:
        if stdout_path is None:
            print(output, file=sys.stderr)
        raise RuntimeError(f"{cmd[0]} failed with exit code {proc.returncode}")


def _run_bibtex(*, pdf_dir: Path) -> None:
    proc = subprocess.run(
        ["bibtex", COMBINED_STEM],
        cwd=str(pdf_dir),
        capture_output=True,
        check=False,
        text=True,
    )
    (pdf_dir / "_bibtex_stdout.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    bbl_path = pdf_dir / f"{COMBINED_STEM}.bbl"
    if proc.returncode != 0 and (not bbl_path.exists() or bbl_path.stat().st_size == 0):
        raise RuntimeError(f"bibtex failed with exit code {proc.returncode} and did not produce a .bbl")


def _pandoc_to_tex(
    *,
    combined_md: Path,
    combined_tex: Path,
    pdf_dir: Path,
    preamble_tex: Path,
    source_manuscript: Path,
    project_root: Path,
) -> None:
    command = [
        "pandoc",
        str(combined_md.name),
        "--from",
        "markdown+raw_tex+tex_math_dollars+fenced_code_attributes+implicit_figures",
        "--to",
        "latex",
        "--standalone",
        "--table-of-contents",
        "--filter",
        "pandoc-crossref",
        "--natbib",
        "--bibliography",
        "references.bib",
        "--output",
        str(combined_tex.name),
        *_metadata_args(source_manuscript=source_manuscript, project_root=project_root),
    ]
    _run(command, cwd=pdf_dir)
    _insert_preamble_into_tex(combined_tex=combined_tex, preamble_tex=preamble_tex)
    _shorten_caption_aux_entries(combined_tex=combined_tex)


def _insert_preamble_into_tex(*, combined_tex: Path, preamble_tex: Path) -> None:
    text = combined_tex.read_text(encoding="utf-8")
    marker = "\\begin{document}"
    if marker not in text:
        raise ValueError(f"{combined_tex} does not contain {marker!r}")
    preamble = preamble_tex.read_text(encoding="utf-8").rstrip()
    combined_tex.write_text(text.replace(marker, f"{preamble}\n\n{marker}", 1), encoding="utf-8")


def _shorten_caption_aux_entries(*, combined_tex: Path) -> None:
    """Keep visible captions but avoid long aux/list entries in LaTeX passes."""

    text = combined_tex.read_text(encoding="utf-8")
    combined_tex.write_text(re.sub(r"\\caption(?=\{)", r"\\caption[]", text), encoding="utf-8")


def _latex_to_pdf(
    *,
    combined_tex: Path,
    pdf_dir: Path,
    pdf_path: Path,
    xelatex_stdout: Path,
) -> Path:
    first_pass = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", combined_tex.name]
    _run(first_pass, cwd=pdf_dir)
    _run_bibtex(pdf_dir=pdf_dir)
    _run(first_pass, cwd=pdf_dir)
    _run(first_pass, cwd=pdf_dir)
    _run(first_pass, cwd=pdf_dir, stdout_path=xelatex_stdout)

    generated = pdf_dir / f"{COMBINED_STEM}.pdf"
    if not generated.exists():
        raise FileNotFoundError(generated)
    shutil.copy2(generated, pdf_path)
    return pdf_path


def render_combined_pdf(*, project_root: Path) -> Path:
    """Render the combined PDF for the project at ``project_root``."""
    pdf_dir = project_root / "output" / "pdf"
    pdf_path = pdf_dir / "actinf_policy_entanglement_lean_combined.pdf"
    combined_md = pdf_dir / f"{COMBINED_STEM}.md"
    combined_tex = pdf_dir / f"{COMBINED_STEM}.tex"
    preamble_tex = pdf_dir / "_preamble.tex"
    xelatex_stdout = pdf_dir / "_xelatex_stdout.log"
    injected_manuscript = project_root / "output" / "manuscript"
    source_manuscript = project_root / "manuscript"

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
    _pandoc_to_tex(
        combined_md=combined_md,
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        preamble_tex=preamble_tex,
        source_manuscript=source_manuscript,
        project_root=project_root,
    )
    return _latex_to_pdf(
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        pdf_path=pdf_path,
        xelatex_stdout=xelatex_stdout,
    )


def main(*, project_root: Path) -> int:
    """Regenerate the injected manuscript and render the combined PDF."""
    code = regenerate_injected_manuscript(project_root=project_root)
    if code != 0:
        return code
    pdf_dir = project_root / "output" / "pdf"
    pdf_path = pdf_dir / "actinf_policy_entanglement_lean_combined.pdf"
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
    "main",
    "regenerate_injected_manuscript",
    "render_combined_pdf",
]
