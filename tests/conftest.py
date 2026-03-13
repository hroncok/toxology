"""Pytest fixtures with actual tox config files."""

from pathlib import Path
from textwrap import dedent

import pytest


@pytest.fixture
def tox_project_toml(tmp_path: Path) -> Path:
    """A project dir with a pyproject.toml tox config (native TOML format)."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        dedent(
            """
            [project]
            name = "fixture-project"
            version = "0.1.0"
            requires-python = ">=3.12"

            [tool.tox]
            env_list = ["py312", "lint"]

            [tool.tox.env.py312]
            deps = ["pytest>=8", "coverage"]
            extras = ["dev"]
            dependency_groups = ["test"]
            commands = [["pytest", "tests"], ["coverage", "report"]]

            [tool.tox.env.lint]
            deps = ["ruff"]
            commands = [["ruff", "check", "."]]
            """
        ).strip()
    )
    return tmp_path


@pytest.fixture
def tox_project_ini(tmp_path: Path) -> Path:
    """A project dir with a tox.ini config."""
    tox_ini = tmp_path / "tox.ini"
    tox_ini.write_text(
        dedent(
            """
            [tox]
            env_list = py312,lint

            [testenv:py312]
            deps = pytest>=8
                coverage
            extras = dev
            dependency_groups = test
            commands = pytest tests
                coverage report

            [testenv:lint]
            deps = ruff
            commands = ruff check .
            """
        ).strip()
    )
    return tmp_path
