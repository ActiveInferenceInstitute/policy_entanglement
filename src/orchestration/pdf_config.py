"""Typed manuscript config for the project-local PDF renderer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def latex_text(value: object) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    text = str(value)
    return "".join(replacements.get(ch, ch) for ch in text)


def latex_href_url(url: str) -> str:
    minimal = {"\\": r"\\", "%": r"\%", "#": r"\#", "&": r"\&"}
    return "".join(minimal.get(ch, ch) for ch in url)


@dataclass(frozen=True)
class ManuscriptConfig:
    raw: Mapping[str, Any]

    @classmethod
    def load(cls, source_manuscript: Path) -> ManuscriptConfig:
        config_path = source_manuscript / "config.yaml"
        if not config_path.exists():
            return cls(raw={})
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return cls(raw=loaded if isinstance(loaded, Mapping) else {})

    @property
    def paper(self) -> Mapping[str, Any]:
        paper = self.raw.get("paper")
        return paper if isinstance(paper, Mapping) else {}

    @property
    def authors(self) -> Sequence[Mapping[str, Any]]:
        authors = self.raw.get("authors")
        if not isinstance(authors, Sequence) or isinstance(authors, str):
            return ()
        return tuple(item for item in authors if isinstance(item, Mapping))

    @property
    def publication(self) -> Mapping[str, Any]:
        publication = self.raw.get("publication")
        return publication if isinstance(publication, Mapping) else {}

    @property
    def metadata(self) -> Mapping[str, Any]:
        metadata = self.raw.get("metadata")
        return metadata if isinstance(metadata, Mapping) else {}

    def pandoc_metadata_args(self, *, project_root: Path) -> list[str]:
        first_author = self.authors[0] if self.authors else {}
        title = str(self.paper.get("title") or project_root.name)
        date = str(self.paper.get("date") or "")
        author_name = str(first_author.get("name") or "")
        metadata = [f"title={title}", f"date={date}"]
        if author_name:
            metadata.append(f"author={author_name}")
        args: list[str] = []
        for item in metadata:
            args.extend(["--metadata", item])
        return args

    def author_block(self) -> str:
        doi = str(self.publication.get("doi") or "")
        version = str(self.paper.get("version") or "")
        license_name = str(self.metadata.get("license") or "")
        repository_url = str(self.publication.get("repository_url") or "")
        repository_label = str(self.publication.get("repository_label") or repository_url)
        journal = str(self.publication.get("journal") or "")
        pub_year = str(self.publication.get("year") or "")

        author_blocks: list[str] = []
        for author in self.authors:
            name = str(author.get("name") or "")
            if not name:
                continue
            parts = [latex_text(name)]
            affils: list[str] = []
            if "affiliations" in author:
                raw = author["affiliations"]
                affils = [str(raw)] if isinstance(raw, str) else [str(item) for item in raw]
            elif "affiliation" in author:
                affils = [str(author["affiliation"])]
            for affil in affils:
                parts.append(f"\\\\\\footnotesize{{{latex_text(affil)}}}")
            if "email" in author:
                parts.append(f"\\\\\\footnotesize{{\\texttt{{{latex_text(author['email'])}}}}}")
            if "orcid" in author:
                orcid = str(author["orcid"])
                parts.append(
                    f"\\\\\\footnotesize{{\\href{{https://orcid.org/{latex_href_url(orcid)}}}{{ORCID: {latex_text(orcid)}}}}}"
                )
            author_blocks.append("".join(parts))

        if not author_blocks:
            return ""

        author_str = " \\\\and ".join(author_blocks)
        extras: list[str] = []
        if doi:
            extras.append(f"\\href{{https://doi.org/{latex_href_url(doi)}}}{{DOI: {latex_text(doi)}}}")
        if version:
            extras.append(f"Version {latex_text(version)}")
        if journal:
            journal_line = latex_text(journal)
            if pub_year:
                journal_line = f"{journal_line} ({latex_text(pub_year)})"
            extras.append(journal_line)
        if license_name:
            extras.append(f"License: {latex_text(license_name)}")
        if repository_url:
            label = latex_text(repository_label or repository_url)
            extras.append(f"\\href{{{latex_href_url(repository_url)}}}{{{label}}}")
        if extras:
            author_str += " \\\\ " + " \\\\ ".join(f"\\footnotesize{{{item}}}" for item in extras)
        return author_str

    def title_page_body(self) -> str:
        title = latex_text(self.paper.get("title") or "")
        subtitle = latex_text(self.paper.get("subtitle") or "")
        if subtitle:
            return "\n".join(
                [
                    r"\begin{titlepage}",
                    r"\centering",
                    r"\vspace*{2cm}",
                    r"{\LARGE\bfseries " + title + r"\par}",
                    r"\vspace{0.75em}",
                    r"{\large " + subtitle + r"\par}",
                    r"\vfill",
                    r"\makeatletter",
                    r"{\@author\par}",
                    r"\vspace{1em}",
                    r"{\@date\par}",
                    r"\makeatother",
                    r"\vfill",
                    r"\end{titlepage}",
                    r"\thispagestyle{empty}",
                ]
            )
        return "\\maketitle\n\\thispagestyle{empty}"
