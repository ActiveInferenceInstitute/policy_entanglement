"""Publication canon checks for source repository and DOI state."""

from __future__ import annotations

import re
from pathlib import Path

CANONICAL_PUBLICATION_DOI = "10.5281/zenodo.20418904"
CANONICAL_ZENODO_RECORD = "https://zenodo.org/records/20418904"
CANONICAL_DOI_URL = f"https://doi.org/{CANONICAL_PUBLICATION_DOI}"
CANONICAL_SOURCE_REPOSITORY = "https://github.com/ActiveInferenceInstitute/policy_entanglement"
WRONG_SOURCE_REPOSITORY = "https://github.com/docxology/policy_entanglement"

DEFAULT_PUBLICATION_METADATA_PATHS = (
    "README.md",
    "docs/README.md",
    "AGENTS.md",
    "CITATION.cff",
    "manuscript/config.yaml",
    "manuscript/refs/citations.yaml",
    "manuscript/1A_part1_introduction.md",
    "manuscript/6C_discussion_and_outlook.md",
)

DEFAULT_PUBLICATION_REPOSITORY_PATHS = (
    *DEFAULT_PUBLICATION_METADATA_PATHS,
    "CONTRIBUTING.md",
    "manuscript/0A_abstract.md",
)

DEFAULT_PUBLICATION_BANNER_PATHS = (
    "README.md",
    "docs/README.md",
    "AGENTS.md",
)

DOI_REQUIRED_PATHS = (
    "README.md",
    "AGENTS.md",
    "docs/README.md",
    "CITATION.cff",
    "manuscript/config.yaml",
)

DOI_PENDING_PHRASES = (
    "public Zenodo DOI pending",
    "Zenodo DOI pending",
    "Zenodo deposit pending",
    "no Zenodo DOI has been minted yet",
    "public source archive are pending",
    "public source archive pending",
    "until a DOI is minted",
    "Public Zenodo DOI pending deposit",
)


def _repository_url_from_config(project_root: Path) -> str:
    config_text = (project_root / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*repository_url:\s*"([^"]*)"\s*$', config_text)
    return match.group(1) if match else ""


def _doi_from_config(project_root: Path) -> str:
    config_text = (project_root / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*doi:\s*"([^"]*)"\s*$', config_text)
    return match.group(1) if match else ""


def publication_metadata_issues(
    project_root: Path,
    *,
    metadata_paths: tuple[str, ...] = DEFAULT_PUBLICATION_METADATA_PATHS,
    repository_paths: tuple[str, ...] = DEFAULT_PUBLICATION_REPOSITORY_PATHS,
    banner_paths: tuple[str, ...] = DEFAULT_PUBLICATION_BANNER_PATHS,
) -> list[str]:
    """Reject contradictory public DOI / source-repository states."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return []
    config_text = config_path.read_text(encoding="utf-8")
    configured_doi = _doi_from_config(project_root)
    doi_is_pending = configured_doi == ""
    repository_is_pending = bool(re.search(r"(?m)^\s*repository_url:\s*\"\"\s*$", config_text))
    issues: list[str] = []

    metadata_files = [project_root / rel for rel in metadata_paths]
    repository_files = [project_root / rel for rel in repository_paths]
    banner_files = [project_root / rel for rel in banner_paths]

    if doi_is_pending:
        for path in metadata_files:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(project_root)
            if CANONICAL_PUBLICATION_DOI in text:
                issues.append(f"{rel}: publishes canonical DOI while config DOI is pending")
            if CANONICAL_ZENODO_RECORD in text:
                issues.append(f"{rel}: publishes Zenodo record while config DOI is pending")
        for path in banner_files:
            if not path.exists():
                continue
            if "**Publication:**" in path.read_text(encoding="utf-8"):
                issues.append(f"{path.relative_to(project_root)}: uses public Publication banner while DOI is pending")
    else:
        if configured_doi != CANONICAL_PUBLICATION_DOI:
            issues.append(f"manuscript/config.yaml: doi {configured_doi!r} != canonical {CANONICAL_PUBLICATION_DOI!r}")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in metadata_files if path.exists())
        for phrase in DOI_PENDING_PHRASES:
            if phrase in combined:
                issues.append(f"config DOI is present but current-facing docs still contain pending phrase: {phrase!r}")
        for rel_path_str in DOI_REQUIRED_PATHS:
            surface_path = project_root / rel_path_str
            if not surface_path.exists():
                issues.append(f"{rel_path_str}: missing required publication surface for configured DOI")
                continue
            text = surface_path.read_text(encoding="utf-8")
            if CANONICAL_PUBLICATION_DOI not in text and CANONICAL_DOI_URL not in text:
                issues.append(f"{rel_path_str}: configured DOI not cited on required publication surface")

    if repository_is_pending:
        for path in metadata_files:
            if not path.exists():
                continue
            if CANONICAL_SOURCE_REPOSITORY in path.read_text(encoding="utf-8"):
                issues.append(
                    f"{path.relative_to(project_root)}: publishes canonical repository while config repository is pending"
                )
    else:
        configured_url = _repository_url_from_config(project_root)
        if configured_url != CANONICAL_SOURCE_REPOSITORY:
            issues.append(
                f"manuscript/config.yaml: repository_url {configured_url!r} != canonical {CANONICAL_SOURCE_REPOSITORY!r}"
            )
        for path in repository_files:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(project_root)
            if WRONG_SOURCE_REPOSITORY in text:
                issues.append(f"{rel}: cites wrong source repository {WRONG_SOURCE_REPOSITORY!r}")
            if "no public repository URL" in text:
                issues.append(f"{rel}: claims no public repository URL while config repository is set")
        combined_banners = "\n".join(path.read_text(encoding="utf-8") for path in banner_files if path.exists())
        if "public source archive pending" in combined_banners:
            issues.append("current-facing banners still describe source archive as pending")

    return issues


__all__ = [
    "CANONICAL_DOI_URL",
    "CANONICAL_PUBLICATION_DOI",
    "CANONICAL_SOURCE_REPOSITORY",
    "CANONICAL_ZENODO_RECORD",
    "DEFAULT_PUBLICATION_BANNER_PATHS",
    "DEFAULT_PUBLICATION_METADATA_PATHS",
    "DEFAULT_PUBLICATION_REPOSITORY_PATHS",
    "DOI_PENDING_PHRASES",
    "DOI_REQUIRED_PATHS",
    "WRONG_SOURCE_REPOSITORY",
    "publication_metadata_issues",
]
