"""Pandoc/XeLaTeX compile helpers for the project-local PDF renderer."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from orchestration.pdf_config import ManuscriptConfig
from orchestration.pdf_tex_patch import postprocess_combined_tex

COMBINED_STEM = "_combined_manuscript"


def run_command(cmd: Sequence[str], *, cwd: Path, stdout_path: Path | None = None) -> None:
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


def run_bibtex(*, pdf_dir: Path) -> None:
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


def insert_preamble_into_tex(*, combined_tex: Path, preamble_tex: Path) -> None:
    text = combined_tex.read_text(encoding="utf-8")
    marker = "\\begin{document}"
    if marker not in text:
        raise ValueError(f"{combined_tex} does not contain {marker!r}")
    preamble = preamble_tex.read_text(encoding="utf-8").rstrip()
    combined_tex.write_text(text.replace(marker, f"{preamble}\n\n{marker}", 1), encoding="utf-8")


def shorten_caption_aux_entries(*, combined_tex: Path) -> None:
    text = combined_tex.read_text(encoding="utf-8")
    combined_tex.write_text(re.sub(r"\\caption(?=\{)", r"\\caption[]", text), encoding="utf-8")


def pandoc_to_tex(
    *,
    combined_md: Path,
    combined_tex: Path,
    pdf_dir: Path,
    preamble_tex: Path,
    config: ManuscriptConfig,
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
        *config.pandoc_metadata_args(project_root=project_root),
    ]
    run_command(command, cwd=pdf_dir)
    insert_preamble_into_tex(combined_tex=combined_tex, preamble_tex=preamble_tex)
    shorten_caption_aux_entries(combined_tex=combined_tex)
    postprocess_combined_tex(combined_tex=combined_tex, config=config)


def latex_to_pdf(
    *,
    combined_tex: Path,
    pdf_dir: Path,
    pdf_path: Path,
    xelatex_stdout: Path,
) -> Path:
    first_pass = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", combined_tex.name]
    run_command(first_pass, cwd=pdf_dir)
    run_bibtex(pdf_dir=pdf_dir)
    run_command(first_pass, cwd=pdf_dir)
    run_command(first_pass, cwd=pdf_dir)
    run_command(first_pass, cwd=pdf_dir, stdout_path=xelatex_stdout)

    generated = pdf_dir / f"{COMBINED_STEM}.pdf"
    if not generated.exists():
        raise FileNotFoundError(generated)
    shutil.copy2(generated, pdf_path)
    return pdf_path
