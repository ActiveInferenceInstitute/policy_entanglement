"""Publication canon checks for source repository and DOI state."""

from __future__ import annotations

import re
from pathlib import Path

UNRESOLVED_PUBLICATION_DOI = "10.5281/zenodo.20301239"
UNRESOLVED_ZENODO_RECORD = "https://zenodo.org/records/20301239"
UNRESOLVED_SOURCE_REPOSITORY = "https://github.com/docxology/policy_entanglement"
CANONICAL_SOURCE_REPOSITORY = UNRESOLVED_SOURCE_REPOSITORY
WRONG_SOURCE_REPOSITORY = "https://github.com/ActiveInferenceInstitute/policy_entanglement"

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


def _repository_url_from_config(project_root: Path) -> str:
    config_text = (project_root / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*repository_url:\s*"([^"]*)"\s*$', config_text)
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
    doi_is_pending = bool(re.search(r"(?m)^\s*doi:\s*\"\"\s*$", config_text))
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
            if UNRESOLVED_PUBLICATION_DOI in text:
                issues.append(f"{rel}: publishes unresolved DOI while config DOI is pending")
            if UNRESOLVED_ZENODO_RECORD in text:
                issues.append(f"{rel}: publishes unresolved Zenodo record while config DOI is pending")
        for path in banner_files:
            if not path.exists():
                continue
            if "**Publication:**" in path.read_text(encoding="utf-8"):
                issues.append(f"{path.relative_to(project_root)}: uses public Publication banner while DOI is pending")
    else:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in metadata_files if path.exists())
        if "no Zenodo DOI has been minted yet" in combined or "public Zenodo DOI" in combined:
            issues.append("config DOI is present but current-facing docs still describe the DOI as pending")

    if repository_is_pending:
        for path in metadata_files:
            if not path.exists():
                continue
            if UNRESOLVED_SOURCE_REPOSITORY in path.read_text(encoding="utf-8"):
                issues.append(
                    f"{path.relative_to(project_root)}: publishes unresolved source repository while config repository is pending"
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
    "CANONICAL_SOURCE_REPOSITORY",
    "DEFAULT_PUBLICATION_BANNER_PATHS",
    "DEFAULT_PUBLICATION_METADATA_PATHS",
    "DEFAULT_PUBLICATION_REPOSITORY_PATHS",
    "UNRESOLVED_PUBLICATION_DOI",
    "UNRESOLVED_SOURCE_REPOSITORY",
    "UNRESOLVED_ZENODO_RECORD",
    "WRONG_SOURCE_REPOSITORY",
    "publication_metadata_issues",
]
