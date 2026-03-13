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


@pytest.fixture
def tox_project_minimal_toml(tmp_path: Path) -> Path:
    """Minimal pyproject.toml tox config: only env_list, no deps/extras/commands."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        dedent(
            """
            [project]
            name = "minimal-project"
            version = "0.1.0"
            requires-python = ">=3.12"

            [tool.tox]
            env_list = ["py312"]

            [tool.tox.env.py312]
            """
        ).strip()
    )
    return tmp_path


@pytest.fixture
def tox_project_setup_cfg(tmp_path: Path) -> Path:
    """A project dir with a setup.cfg tox config ([tox:tox] section)."""
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        dedent(
            """
            [tox:tox]
            env_list = py312,lint

            [testenv:py312]
            deps = pytest>=8
            commands = pytest

            [testenv:lint]
            deps = ruff
            commands = ruff check .
            """
        ).strip()
    )
    return tmp_path
