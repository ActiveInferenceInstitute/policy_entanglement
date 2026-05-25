"""Unit tests for :mod:`orchestration.build_pdf` and :mod:`orchestration.run_all`."""

from __future__ import annotations

import hashlib
from pathlib import Path

from orchestration.build_pdf import (
    COMBINED_STEM,
    _discover_manuscript_files,
    _mirror_render_auxiliary_files,
    _normalise_render_paths,
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
    (ms / "99_bibliography.md").write_text("# Bib\n", encoding="utf-8")
    (ms / "preamble.md").write_text("skip\n", encoding="utf-8")
    files = _discover_manuscript_files(ms)
    assert [p.name for p in files] == ["01_a.md", "99_bibliography.md"]
    combined = tmp_path / "out.md"
    _write_combined_markdown(files, combined_md=combined)
    assert "A" in combined.read_text(encoding="utf-8")


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
