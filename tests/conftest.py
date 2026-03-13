"""Pytest fixtures with actual tox config files."""

import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _copy_fixture(name: str, dest: Path) -> None:
    """Copy fixture directory from tests/fixtures/{name}/ into dest."""
    src = FIXTURES_DIR / name
    for path in src.iterdir():
        if path.is_file():
            shutil.copy(path, dest / path.name)


def _make_fixture(name: str):
    """Return a pytest fixture that copies tests/fixtures/{name}/ into tmp_path."""

    @pytest.fixture
    def fixture(tmp_path: Path) -> Path:
        _copy_fixture(name, tmp_path)
        return tmp_path

    fixture.__name__ = name
    return fixture


# Create a fixture for each directory in tests/fixtures
for _path in sorted(FIXTURES_DIR.iterdir()):
    if _path.is_dir():
        globals()[_path.name] = _make_fixture(_path.name)
