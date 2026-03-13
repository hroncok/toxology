"""Tests for read_tox_config using fixtures with actual tox config files."""

import ast
import linecache
from pathlib import Path

import pytest

# this is a private API but it has been available here at least since pytest 1.0.0
from _pytest.assertion.rewrite import rewrite_asserts

from toxology import ToxCommand, ToxEnvConfig, read_tox_config


class TestReadToxConfigToml:
    """Tests using pyproject.toml (native TOML) tox config."""

    def test_returns_tox_env_config(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert isinstance(config, ToxEnvConfig)
        assert config.name == "py312"

    def test_deps_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert "pytest>=8" in config.deps
        assert "coverage" in config.deps
        assert len(config.deps) == 2

    def test_extras_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert "dev" in config.extras

    def test_dependency_groups_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert "test" in config.dependency_groups

    def test_commands_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert len(config.commands) == 2
        assert config.commands[0].args == ("pytest", "tests")
        assert config.commands[1].args == ("coverage", "report")

    def test_lint_env_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("lint", path=tox_project_toml)
        assert config.name == "lint"
        assert "ruff" in config.deps
        assert config.commands[0].args == ("ruff", "check", ".")

    def test_convenience_properties(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert config.deps_list == list(config.deps)
        assert config.extras_set == set(config.extras)
        assert config.dependency_groups_set == set(config.dependency_groups)
        assert config.commands_list == list(config.commands)


class TestReadToxConfigIni:
    """Tests using tox.ini config."""

    def test_returns_tox_env_config(self, tox_project_ini: Path) -> None:
        config = read_tox_config("py312", path=tox_project_ini)
        assert isinstance(config, ToxEnvConfig)
        assert config.name == "py312"

    def test_deps_from_ini(self, tox_project_ini: Path) -> None:
        config = read_tox_config("py312", path=tox_project_ini)
        assert "pytest>=8" in config.deps
        assert "coverage" in config.deps

    def test_commands_from_ini(self, tox_project_ini: Path) -> None:
        config = read_tox_config("py312", path=tox_project_ini)
        assert any(cmd.args == ("pytest", "tests") for cmd in config.commands)
        assert any(cmd.args == ("coverage", "report") for cmd in config.commands)

    def test_lint_env_from_ini(self, tox_project_ini: Path) -> None:
        config = read_tox_config("lint", path=tox_project_ini)
        assert config.name == "lint"
        assert "ruff" in config.deps


class TestReadToxConfigSetupCfg:
    """Tests using setup.cfg tox config ([tox:tox] section)."""

    def test_returns_tox_env_config(self, tox_project_setup_cfg: Path) -> None:
        config = read_tox_config("py312", path=tox_project_setup_cfg)
        assert isinstance(config, ToxEnvConfig)
        assert config.name == "py312"

    def test_deps_from_setup_cfg(self, tox_project_setup_cfg: Path) -> None:
        config = read_tox_config("py312", path=tox_project_setup_cfg)
        assert "pytest>=8" in config.deps

    def test_commands_from_setup_cfg(self, tox_project_setup_cfg: Path) -> None:
        config = read_tox_config("py312", path=tox_project_setup_cfg)
        assert any(cmd.args == ("pytest",) for cmd in config.commands)

    def test_lint_env_from_setup_cfg(self, tox_project_setup_cfg: Path) -> None:
        config = read_tox_config("lint", path=tox_project_setup_cfg)
        assert config.name == "lint"
        assert "ruff" in config.deps
        assert any(cmd.args == ("ruff", "check", ".") for cmd in config.commands)


class TestDefaultPath:
    """Tests for default path (path=None uses cwd)."""

    def test_default_path_uses_cwd(
        self, tox_project_toml: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When path is not passed, config is read from current working directory."""
        monkeypatch.chdir(tox_project_toml)
        config = read_tox_config("py312")
        assert config.name == "py312"
        assert "pytest>=8" in config.deps


class TestMinimalConfig:
    """Tests for configs with missing extras, deps, dependency_groups, or commands."""

    def test_minimal_toml_returns_empty_deps(self, tox_project_minimal_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        assert config.deps == ()

    def test_minimal_toml_returns_empty_extras(self, tox_project_minimal_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        assert config.extras == frozenset()

    def test_minimal_toml_returns_empty_dependency_groups(
        self, tox_project_minimal_toml: Path
    ) -> None:
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        assert config.dependency_groups == frozenset()

    def test_minimal_toml_returns_empty_commands(self, tox_project_minimal_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        assert config.commands == ()

    def test_minimal_toml_has_name(self, tox_project_minimal_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        assert config.name == "py312"


class TestReadmeExample:
    """Test the documented example: TOML config + code-with-asserts from README."""

    @staticmethod
    def _extract_fenced_block(text: str, lang: str) -> str:
        """Return the content of the first ```lang ... ``` block in text."""
        marker = f"```{lang}\n"
        start = text.find(marker)
        assert start >= 0, f"README has no {lang} code block"
        content_start = start + len(marker)
        content_end = text.find("\n```", content_start)
        assert content_end > content_start, f"README {lang} block not closed"
        return text[content_start:content_end]

    @staticmethod
    def _exec_with_pytest_asserts(code: str, namespace: dict, filename: str) -> None:
        """Run code with pytest assertion rewriting and source in linecache for friendly tracebacks."""
        tree = ast.parse(code)
        rewrite_asserts(tree, code.encode(), filename)
        linecache.cache[filename] = (
            len(code),
            None,  # mtime: no real file, so no invalidation by modification time
            code.splitlines(keepends=True),
            filename,
        )
        exec(compile(tree, filename, "exec"), namespace)

    def test_readme_example_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Parse README's example TOML and code block; create config, run code with asserts."""
        readme = Path(__file__).resolve().parent.parent / "README.md"
        text = readme.read_text()
        toml_block = self._extract_fenced_block(text, "toml")
        python_block = self._extract_fenced_block(text, "python")

        (tmp_path / "pyproject.toml").write_text(toml_block)
        monkeypatch.chdir(tmp_path)
        namespace: dict = {"read_tox_config": read_tox_config}
        self._exec_with_pytest_asserts(python_block, namespace, "<README example>")
        # Assertions are in the executed block; if we get here without exception, test passes


class TestToxCommand:
    """Tests for ToxCommand."""

    def test_shell_property(self) -> None:
        cmd = ToxCommand(args=("pytest", "tests"))
        shell = cmd.shell
        assert "pytest" in shell
        assert "tests" in shell
