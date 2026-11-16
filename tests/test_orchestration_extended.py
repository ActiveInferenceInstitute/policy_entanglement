"""Extended coverage for orchestration.build_pdf and orchestration.run_all."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from orchestration import build_pdf as bp
from orchestration import run_all as ra
from orchestration.build_pdf import COMBINED_STEM, render_combined_pdf
from orchestration.run_all import StageSummary
from orchestration.run_all import main as run_all_main

PROJECT = Path(__file__).resolve().parent.parent


def test_build_parser_flag_matrix() -> None:
    parser = ra.build_parser()
    args = parser.parse_args(["--serial", "--with-pdf", "--with-mathlib", "--only", "build_lean", "--skip", "x"])
    assert args.serial is True
    assert args.with_pdf is True
    assert args.with_mathlib is True
    assert args.only == ["build_lean"]
    assert args.skip == ["x"]


def test_insert_preamble_into_tex_and_clean_artifacts(tmp_path: Path) -> None:
    tex = tmp_path / "doc.tex"
    tex.write_text("\\documentclass{article}\n\\begin{document}\n\\end{document}\n", encoding="utf-8")
    pre = tmp_path / "pre.tex"
    pre.write_text("% preamble\n\\usepackage{x}\n", encoding="utf-8")
    bp._insert_preamble_into_tex(combined_tex=tex, preamble_tex=pre)
    merged = tex.read_text(encoding="utf-8")
    assert "\\usepackage{x}" in merged
    assert merged.index("\\usepackage{x}") < merged.index("\\begin{document}")

    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / f"{COMBINED_STEM}.aux").write_text("x", encoding="utf-8")
    pdf_path = pdf_dir / "out.pdf"
    pdf_path.write_bytes(b"pdf")
    bp._clean_combined_artifacts(
        pdf_dir=pdf_dir,
        pdf_path=pdf_path,
        preamble_tex=tmp_path / "p.tex",
        xelatex_stdout=tmp_path / "log.txt",
    )
    assert not (pdf_dir / f"{COMBINED_STEM}.aux").exists()
    assert not pdf_path.exists()


def test_run_raises_on_failure(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="failed"):
        bp._run(["false"], cwd=tmp_path)


def test_insert_preamble_missing_marker_raises(tmp_path: Path) -> None:
    tex = tmp_path / "bad.tex"
    tex.write_text("\\foo\n", encoding="utf-8")
    pre = tmp_path / "pre.tex"
    pre.write_text("% p\n", encoding="utf-8")
    with pytest.raises(ValueError, match="begin{document}"):
        bp._insert_preamble_into_tex(combined_tex=tex, preamble_tex=pre)


def test_drop_inert_table_caption_setup(tmp_path: Path) -> None:
    """Pandoc's float-table caption skip goes only when no table float exists."""
    tex = tmp_path / "doc.tex"
    setup = "\\usepackage{longtable,booktabs,array}\n\\usepackage{caption}\n\\captionsetup[table]{skip=6pt}\n"
    tex.write_text(setup + "\\begin{document}\n\\begin{longtable}{ll}a&b\\\\\\end{longtable}\n\\end{document}\n")
    bp._drop_inert_table_caption_setup(combined_tex=tex)
    stripped = tex.read_text(encoding="utf-8")
    assert "\\captionsetup[table]" not in stripped
    assert "\\usepackage{caption}" in stripped

    tex.write_text(setup + "\\begin{document}\n\\begin{table}\\caption{x}\\end{table}\n\\end{document}\n")
    bp._drop_inert_table_caption_setup(combined_tex=tex)
    assert "\\captionsetup[table]{skip=6pt}" in tex.read_text(encoding="utf-8")


def test_run_bibtex_writes_log(tmp_path: Path) -> None:
    if shutil.which("bibtex") is None:
        pytest.skip("bibtex not on PATH")
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / f"{COMBINED_STEM}.aux").write_text("\\citation{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        bp._run_bibtex(pdf_dir=pdf_dir)
    assert (pdf_dir / "_bibtex_stdout.log").exists()


def _seed_minimal_injected_manuscript(project_root: Path) -> None:
    ms = project_root / "manuscript"
    injected = project_root / "output" / "manuscript"
    for d in (ms, injected):
        d.mkdir(parents=True, exist_ok=True)
        (d / "preamble.md").write_text("```latex\n\\usepackage{x}\n```\n", encoding="utf-8")
        (d / "config.yaml").write_text("paper:\n  title: T\n", encoding="utf-8")
        (d / "01_intro.md").write_text("# Intro\n\nBody.\n", encoding="utf-8")


def test_render_combined_pdf_no_injected_files(tmp_path: Path) -> None:
    _seed_minimal_injected_manuscript(tmp_path)
    (tmp_path / "output" / "manuscript").glob("*.md")
    for p in list((tmp_path / "output" / "manuscript").glob("*.md")):
        if p.name != "preamble.md":
            p.unlink()
    with pytest.raises(FileNotFoundError, match="no injected manuscript"):
        render_combined_pdf(project_root=tmp_path)


def test_render_combined_pdf_stubs_latex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_minimal_injected_manuscript(tmp_path)

    def _fake_pandoc(**kwargs: object) -> None:
        combined_tex = kwargs["combined_tex"]
        assert isinstance(combined_tex, Path)
        combined_tex.write_text(
            "\\documentclass{article}\n\\begin{document}\nHi\n\\end{document}\n",
            encoding="utf-8",
        )

    def _touch_pdf(**kwargs: object) -> Path:
        path = kwargs["pdf_path"]
        assert isinstance(path, Path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF-1.4")
        (path.parent / f"{COMBINED_STEM}.pdf").write_bytes(b"%PDF-1.4")
        return path

    monkeypatch.setattr(bp, "_pandoc_to_tex", _fake_pandoc)
    monkeypatch.setattr(bp, "_latex_to_pdf", _touch_pdf)
    out = render_combined_pdf(project_root=tmp_path)
    assert out.name.endswith("_combined.pdf")
    assert (tmp_path / "output" / "pdf" / f"{COMBINED_STEM}.md").exists()
    assert (tmp_path / "output" / "pdf" / f"{COMBINED_STEM}.tex").exists()


def test_run_all_main_only_ok_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "ok.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    monkeypatch.setattr(ra, "SCRIPTS", [("ok.py", "ok stage")])
    monkeypatch.setattr(ra, "PARALLEL_STAGE_STEMS", frozenset())
    code = run_all_main(["--only", "ok", "--no-manifest"], project_root=tmp_path, scripts_dir=scripts)
    assert code == 0


def test_run_all_main_records_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "bad.py").write_text("import sys\nsys.exit(2)\n", encoding="utf-8")
    monkeypatch.setattr(ra, "SCRIPTS", [("bad.py", "bad stage")])
    monkeypatch.setattr(ra, "PARALLEL_STAGE_STEMS", frozenset())
    code = run_all_main(["--only", "bad", "--no-manifest"], project_root=tmp_path, scripts_dir=scripts)
    assert code == 1


def test_run_all_parallel_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("a.py", "b.py"):
        (scripts / name).write_text("print('x')\n", encoding="utf-8")
    monkeypatch.setattr(ra, "SCRIPTS", [("a.py", "a"), ("b.py", "b")])
    monkeypatch.setattr(ra, "PARALLEL_STAGE_STEMS", frozenset({"a", "b"}))
    code = run_all_main(["--no-manifest"], project_root=tmp_path, scripts_dir=scripts)
    assert code == 0


def test_render_combined_pdf_copies_references_bib(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_minimal_injected_manuscript(tmp_path)
    bib = tmp_path / "output" / "manuscript" / "references.bib"
    bib.write_text("@article{a, title={t}}\n", encoding="utf-8")

    def _fake_pandoc(**kwargs: object) -> None:
        combined_tex = kwargs["combined_tex"]
        assert isinstance(combined_tex, Path)
        combined_tex.write_text("\\documentclass{article}\n\\begin{document}\n\\end{document}\n", encoding="utf-8")

    def _touch_pdf(**kwargs: object) -> Path:
        path = kwargs["pdf_path"]
        assert isinstance(path, Path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF-1.4")
        return path

    monkeypatch.setattr(bp, "_pandoc_to_tex", _fake_pandoc)
    monkeypatch.setattr(bp, "_latex_to_pdf", _touch_pdf)
    render_combined_pdf(project_root=tmp_path)
    assert (tmp_path / "output" / "pdf" / "references.bib").exists()


def test_latex_to_pdf_with_stubbed_xelatex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    combined_tex = pdf_dir / f"{COMBINED_STEM}.tex"
    combined_tex.write_text("\\documentclass{article}\n\\begin{document}\n\\end{document}\n", encoding="utf-8")
    pdf_path = pdf_dir / "out.pdf"
    log_path = pdf_dir / "log.txt"

    def _fake_run(cmd, *, cwd, stdout_path=None):
        (cwd / f"{COMBINED_STEM}.pdf").write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(bp, "_run", _fake_run)
    monkeypatch.setattr(bp, "_run_bibtex", lambda **_: None)
    produced = bp._latex_to_pdf(
        combined_tex=combined_tex,
        pdf_dir=pdf_dir,
        pdf_path=pdf_path,
        xelatex_stdout=log_path,
    )
    assert produced == pdf_path
    assert pdf_path.exists()


def test_run_all_pre_regression_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A real downstream audit sees its producer's bytes before finalization."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (tmp_path / "input.json").write_text("[2, 5]", encoding="utf-8")
    (scripts / "ok.py").write_text(
        "import json\nfrom pathlib import Path\n"
        "numbers = json.loads(Path('input.json').read_text())\n"
        "out = Path('output/data/summary.json')\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text(json.dumps({'total': sum(numbers)}))\n",
        encoding="utf-8",
    )
    (scripts / "regression_gate.py").write_text(
        "import hashlib, json\nfrom pathlib import Path\n"
        "content = Path('output/data/summary.json').read_bytes()\n"
        "manifest = Path('output/MANIFEST.md').read_text()\n"
        "row = next(line for line in manifest.splitlines() if '`output/data/summary.json`' in line)\n"
        "assert hashlib.sha256(content).hexdigest() in row\n"
        "assert int(row.split('|')[2].strip()) == len(content)\n"
        "stage = next(line for line in manifest.splitlines() if '`ok.py`' in line)\n"
        "assert stage.split('|')[3].strip() == 'OK'\n"
        "Path('output/audited.json').write_text(json.dumps({'observed_total': json.loads(content)['total']}))\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ra, "SCRIPTS", [("ok.py", "produce summary"), ("regression_gate.py", "audit bytes")])
    code = run_all_main(
        ["--serial", "--only", "ok", "--only", "regression_gate"], project_root=tmp_path, scripts_dir=scripts
    )
    assert code == 0
    assert json.loads((tmp_path / "output/audited.json").read_text()) == {"observed_total": 7}
    final = (tmp_path / "output/MANIFEST.md").read_text()
    assert "`output/audited.json`" in final


def test_write_manifest_large_file_skips_hash(tmp_path: Path) -> None:
    output = tmp_path / "output"
    big = output / "data" / "big.bin"
    big.parent.mkdir(parents=True)
    big.write_bytes(b"x" * (ra._SHA256_MAX_BYTES + 1))
    manifest = ra._write_manifest(
        project_root=tmp_path,
        run_summary={
            "stages": [StageSummary(script="ok.py", duration_s=1.0, returncode=0)],
            "total_wall_s": 1.0,
        },
    )
    text = manifest.read_text(encoding="utf-8")
    assert "skipped: >8 MB" in text


def _summary_stage(root: Path) -> Path:
    scripts = root / "scripts"
    scripts.mkdir()
    (root / "input.json").write_text("[4, 7]", encoding="utf-8")
    (scripts / "fixture.py").write_text(
        "import json\nfrom pathlib import Path\n"
        "values = json.loads(Path('input.json').read_text())\n"
        "out = Path('output/total.json')\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text(json.dumps({'total': sum(values)}))\n",
        encoding="utf-8",
    )
    return scripts


@pytest.mark.parametrize(
    "selection",
    [
        ["--only", "unknown"],
        ["--skip", "unknown"],
        ["--only", "fixture", "--only", "unknown"],
        ["--only", "fixture", "--skip", "unknown"],
    ],
)
def test_unknown_stages_fail_before_artifact_or_manifest_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, selection: list[str]
) -> None:
    scripts = _summary_stage(tmp_path)
    monkeypatch.setattr(ra, "SCRIPTS", [("fixture.py", "sum actual input")])
    output = tmp_path / "output"
    output.mkdir()
    manifest = output / "MANIFEST.md"
    manifest.write_bytes(b"existing inventory\n")
    with pytest.raises(SystemExit) as error:
        run_all_main(selection, project_root=tmp_path, scripts_dir=scripts)
    assert error.value.code == 2
    assert manifest.read_bytes() == b"existing inventory\n"
    assert sorted(path.name for path in output.iterdir()) == ["MANIFEST.md"]


def test_known_optional_skip_does_not_activate_or_reject_the_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripts = _summary_stage(tmp_path)
    monkeypatch.setattr(ra, "SCRIPTS", [("fixture.py", "sum actual input")])
    assert run_all_main(
        ["--serial", "--only", "fixture", "--skip", "build_pdf", "--skip", "readiness_report"],
        project_root=tmp_path,
        scripts_dir=scripts,
    ) == 0
    assert json.loads((tmp_path / "output/total.json").read_text()) == {"total": 11}
    manifest = (tmp_path / "output/MANIFEST.md").read_text()
    assert "`fixture.py`" in manifest
    assert "`build_pdf.py`" not in manifest
    assert "`readiness_report.py`" not in manifest


def test_known_selection_fully_filtered_by_skip_executes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripts = _summary_stage(tmp_path)
    monkeypatch.setattr(ra, "SCRIPTS", [("fixture.py", "sum actual input")])
    assert run_all_main(
        ["--only", "fixture", "--skip", "fixture"], project_root=tmp_path, scripts_dir=scripts
    ) == 0
    assert not (tmp_path / "output").exists()
    assert (tmp_path / "input.json").read_text() == "[4, 7]"
