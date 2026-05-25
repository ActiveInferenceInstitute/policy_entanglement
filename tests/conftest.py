"""Shared pytest fixtures for actinf_policy_entanglement_lean."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def actinf_project_root() -> Path:
    return PROJECT


@pytest.fixture(scope="session")
def lake_available() -> bool:
    return shutil.which("lake") is not None
