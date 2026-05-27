"""Unit tests for :mod:`orchestration.build_pdf` and :mod:`orchestration.run_all`."""

from __future__ import annotations

import hashlib
from pathlib import Path

from orchestration.build_pdf import (
    COMBINED_STEM,
    _author_block_from_config,
    _discover_manuscript_files,
    _mirror_render_auxiliary_files,
    _normalise_render_paths,
    _patch_red_hyperlinks,
    _postprocess_combined_tex,
    _section_sort_key,
    _write_combined_markdown,
)
from orchestration.run_all import _write_manifest, build_parser

PROJECT = Path(__file__).resolve().parent.parent


def test_section_sort_key_puts_bibliography_last() -> None:
    assert _section_sort_key(Path("01_intro.md")) < _section_sort_key(Path("99_bibliography.md"))


def test_normalise_render_paths_rewrites_figure_prefix() -> None:
    text = "![x](../output/figures/plot.png)"
    assert "../figures/plot.png" in _normalise_render_paths(text)


def test_discover_and_combine_markdown(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "01_a.md").write_text("# A\n", encoding="utf-8")
    (ms / "00_abstract.md").write_text("# Abstract\n", encoding="utf-8")
    (ms / "99_bibliography.md").write_text("# Bib\n", encoding="utf-8")
    (ms / "preamble.md").write_text("skip\n", encoding="utf-8")
    files = _discover_manuscript_files(ms)
    assert [p.name for p in files] == ["01_a.md", "99_bibliography.md"]
    combined = tmp_path / "out.md"
    _write_combined_markdown(files, combined_md=combined)
    assert "A" in combined.read_text(encoding="utf-8")
    assert "Abstract" not in combined.read_text(encoding="utf-8")


def test_patch_red_hyperlinks_replaces_hidelinks() -> None:
    tex = "\\hypersetup{\n  hidelinks,\n  pdfcreator={LaTeX via pandoc}}\n"
    patched = _patch_red_hyperlinks(tex)
    assert "hidelinks" not in patched
    assert "linkcolor=red" in patched


def test_author_block_from_config_includes_metadata() -> None:
    config = {
        "paper": {"title": "T", "subtitle": "S", "version": "1.0"},
        "authors": [
            {
                "name": "Author",
                "email": "a@example.com",
                "orcid": "0000-0001-0000-0000",
                "affiliation": "Institute",
            }
        ],
        "publication": {
            "doi": "10.5281/zenodo.123",
            "repository_url": "https://github.com/org/repo",
            "repository_label": "Source repository",
            "journal": "Journal",
            "year": "2026",
        },
        "metadata": {"license": "CC-BY-4.0"},
    }
    block = _author_block_from_config(config)
    assert "Author" in block
    assert "a@example.com" in block
    assert "ORCID" in block
    assert "10.5281/zenodo.123" in block
    assert "Version 1.0" in block
    assert "CC-BY-4.0" in block


def test_postprocess_combined_tex_injects_author_and_titlepage(tmp_path: Path) -> None:
    ms = tmp_path / "manuscript"
    ms.mkdir()
    (ms / "config.yaml").write_text(
        "paper:\n  title: Title\n  subtitle: Sub\n  version: '1.0'\n"
        "authors:\n  - name: Author\n    email: a@example.com\n    orcid: '0000-0001-0000-0000'\n"
        "    affiliation: Lab\n"
        "publication:\n  doi: 10.5281/zenodo.1\n",
        encoding="utf-8",
    )
    tex = tmp_path / "doc.tex"
    tex.write_text(
        "\\hypersetup{hidelinks,}\n\\author{Author}\n\\date{}\n\\begin{document}\n\\maketitle\n",
        encoding="utf-8",
    )
    _postprocess_combined_tex(combined_tex=tex, source_manuscript=ms)
    out = tex.read_text(encoding="utf-8")
    assert "hidelinks" not in out
    assert "linkcolor=red" in out
    assert "a@example.com" in out
    assert "ORCID" in out
    assert "10.5281/zenodo.1" in out
    assert "\\begin{titlepage}" in out
    assert "\\maketitle" not in out


def test_mirror_render_auxiliary_files(tmp_path: Path) -> None:
    src = tmp_path / "src_ms"
    dst = tmp_path / "dst_ms"
    src.mkdir()
    dst.mkdir()
    (src / "config.yaml").write_text("paper:\n  title: t\n", encoding="utf-8")
    (src / "preamble.md").write_text("% tex\n", encoding="utf-8")
    _mirror_render_auxiliary_files(source_manuscript=src, injected_manuscript=dst)
    assert (dst / "config.yaml").exists()
    assert (dst / "preamble.md").read_text(encoding="utf-8") == "% tex\n"


def test_combined_stem_constant() -> None:
    assert COMBINED_STEM == "_combined_manuscript"


def test_run_all_build_parser_accepts_pdf_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(["--with-pdf"])
    assert args.with_pdf is True


def test_write_manifest_excludes_ds_store(tmp_path: Path) -> None:
    output = tmp_path / "output"
    data_dir = output / "data"
    data_dir.mkdir(parents=True)
    legitimate = data_dir / "payload.json"
    legitimate.write_text('{"ok": true}\n', encoding="utf-8")
    (output / ".DS_Store").write_bytes(b"finder metadata")

    manifest = _write_manifest(
        project_root=tmp_path,
        run_summary={"stages": [{"script": "example.py", "duration_s": 1.0, "returncode": 0}], "total_wall_s": 1.0},
    )
    text = manifest.read_text(encoding="utf-8")
    digest = hashlib.sha256(legitimate.read_bytes()).hexdigest()
    assert digest in text
    assert "output/.DS_Store" not in text
