"""Shared pytest fixtures and path helpers for the Crosswalk test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

# Repo root = directory containing this conftest.
REPO_ROOT = Path(__file__).resolve().parent
FIXTURES = REPO_ROOT / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Absolute path to the ``fixtures/`` directory."""
    return FIXTURES
