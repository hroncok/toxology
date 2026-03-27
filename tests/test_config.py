"""Tests for read_tox_config using fixtures with actual tox config files."""

import ast
import linecache
import sys
from pathlib import Path

import pytest

# this is a private API but it has been available here at least since pytest 1.0.0
from _pytest.assertion.rewrite import rewrite_asserts

from toxology import ToxEnvConfig, read_tox_config


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
        assert tuple(config.commands[0].args) == ("pytest", "tests")
        assert tuple(config.commands[1].args) == ("coverage", "report")

    def test_lint_env_from_toml(self, tox_project_toml: Path) -> None:
        config = read_tox_config("lint", path=tox_project_toml)
        assert config.name == "lint"
        assert "ruff" in config.deps
        assert tuple(config.commands[0].args) == ("ruff", "check", ".")

    def test_convenience_properties(self, tox_project_toml: Path) -> None:
        config = read_tox_config("py312", path=tox_project_toml)
        assert config.deps_list == list(config.deps)
        assert config.extras_set == set(config.extras)
        assert config.dependency_groups_set == set(config.dependency_groups)
        assert config.commands_list == list(config.commands)

    def test_no_virtualenv_created(self, tox_project_toml: Path) -> None:
        """Reading config must not create a .tox virtual environment."""
        read_tox_config("py312", path=tox_project_toml)
        assert not (tox_project_toml / ".tox").exists()


class TestReadToxConfigMinversion:
    """Config with minversion = 666; we only read config, so it should still work."""

    def test_minversion_666_still_readable(self, tox_project_minversion_666: Path) -> None:
        """Reading config does not run tox, so an impossible minversion does not block us."""
        config = read_tox_config("py312", path=tox_project_minversion_666)
        assert config.name == "py312"
        assert "pytest" in config.deps
        assert tuple(config.commands[0].args) == ("pytest",)


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
        assert any(tuple(c.args) == ("pytest", "tests") for c in config.commands)
        assert any(tuple(c.args) == ("coverage", "report") for c in config.commands)

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
        assert any(tuple(c.args) == ("pytest",) for c in config.commands)

    def test_lint_env_from_setup_cfg(self, tox_project_setup_cfg: Path) -> None:
        config = read_tox_config("lint", path=tox_project_setup_cfg)
        assert config.name == "lint"
        assert "ruff" in config.deps
        assert any(tuple(c.args) == ("ruff", "check", ".") for c in config.commands)


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


class TestEnvConfWithoutExtrasKeys:
    """When tox env conf does not define 'extras' or 'dependency_groups' (e.g. tox.ini-only)."""

    def test_ini_no_extras_returns_empty_extras_and_dependency_groups(
        self, tox_project_ini_no_extras: Path
    ) -> None:
        """Config without extras/dependency_groups (tox.ini only) does not KeyError; returns empty."""
        config = read_tox_config("py314", path=tox_project_ini_no_extras)
        assert config.extras == frozenset()
        assert config.dependency_groups == frozenset()
        assert config.name == "py314"
        assert "pytest" in config.deps
        assert len(config.commands) >= 1


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


class TestEnvPlaceholdersReplacedWithSysPrefix:
    """Commands that use {envpython}, {envtmpdir} etc. get the tox env path replaced with sys.prefix."""

    def test_commands_contain_sys_prefix_not_tox_env(
        self, tox_project_ini_env_placeholders: Path
    ) -> None:
        """Command args have env placeholders resolved to sys.prefix by virtualenv stubs."""
        # Read config for the same Python version that's running this test
        env_name = f"py{sys.version_info.major}{sys.version_info.minor}"
        config = read_tox_config(env_name, path=tox_project_ini_env_placeholders)
        assert len(config.commands) == 2
        # First command: {envpython} -c "print(1)" -> path under sys.prefix, -c, print(1)
        assert config.commands[0].args[0].startswith(sys.prefix)
        assert tuple(config.commands[0].args[1:]) == ("-c", "print(1)")
        # Second command: echo {envtmpdir} -> echo, path under sys.prefix
        assert config.commands[1].args[0] == "echo"
        assert config.commands[1].args[1].startswith(sys.prefix)


class TestSetenvExtraction:
    """Tests for setenv extraction."""

    def test_setenv_extracted(self, tox_project_with_setenv: Path) -> None:
        """Setenv is extracted from tox config."""
        config = read_tox_config("py312", path=tox_project_with_setenv)
        assert "PYTHONHASHSEED" in config.setenv
        assert config.setenv["PYTHONHASHSEED"] == "42"
        assert "TEST_VAR" in config.setenv
        assert config.setenv["TEST_VAR"] == "test_value"

    def test_empty_setenv_returns_tox_defaults(self, tox_project_minimal_toml: Path) -> None:
        """Config without user setenv still has tox defaults."""
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        # Tox always adds these defaults
        assert "PYTHONIOENCODING" in config.setenv
        assert config.setenv["PYTHONIOENCODING"] == "utf-8"
        # User-specified values should not be present
        assert "TEST_VAR" not in config.setenv


class TestChangedirExtraction:
    """Tests for changedir extraction."""

    def test_changedir_extracted(self, tox_project_with_changedir: Path) -> None:
        """Changedir is extracted from tox config."""
        config = read_tox_config("py312", path=tox_project_with_changedir)
        assert config.changedir is not None
        assert config.changedir.name == "tests"

    def test_no_changedir_returns_project_root(self, tox_project_minimal_toml: Path) -> None:
        """Config without changedir defaults to project root."""
        config = read_tox_config("py312", path=tox_project_minimal_toml)
        # Tox defaults changedir to project root (toxinidir) when not specified
        assert config.changedir == tox_project_minimal_toml


class TestVendoringVerification:
    """Verify vendoring works correctly."""

    def test_vendor_py_script_exists(self) -> None:
        """Vendor script should exist and be executable."""
        vendor_script = Path(__file__).parent.parent / "vendor.py"
        assert vendor_script.exists(), "vendor.py script not found"
        assert vendor_script.is_file(), "vendor.py is not a file"

    def test_vendor_txt_exists(self) -> None:
        """vendor.txt should document what's vendored."""
        vendor_txt = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "vendor.txt"
        assert vendor_txt.exists(), "vendor.txt not found"
        content = vendor_txt.read_text()
        assert "tox==" in content, "vendor.txt doesn't document tox version"
        assert "Vendored at:" in content, "vendor.txt doesn't document vendoring date"

    def test_vendored_tox_exists(self) -> None:
        """Vendored tox package should exist."""
        tox_dir = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox"
        assert tox_dir.exists(), "Vendored tox directory not found"
        assert tox_dir.is_dir(), "Vendored tox is not a directory"
        # Check for key files
        assert (tox_dir / "__init__.py").exists(), "tox/__init__.py not found"
        assert (tox_dir / "plugin" / "manager.py").exists(), "tox/plugin/manager.py not found"

    def test_patches_applied(self) -> None:
        """Verify patches are applied to vendored tox."""
        manager_py = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox" / "plugin" / "manager.py"
        content = manager_py.read_text()
        assert "# TOXOLOGY:" in content, "TOXOLOGY comment marker not found in manager.py"
        assert "Skip external plugins" in content, "External plugin patch not applied"

        sets_py = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox" / "config" / "sets.py"
        content = sets_py.read_text()
        assert "# TOXOLOGY:" in content, "TOXOLOGY comment marker not found in sets.py"


class TestImportIsolation:
    """Test that MetaPathFinder provides proper import isolation."""

    def test_finder_installed_in_meta_path(self) -> None:
        """Ensure our finder is installed in sys.meta_path."""
        import sys
        from toxology._stubs import install_import_hook

        install_import_hook()

        # Finder should be first in meta_path
        finder = sys.meta_path[0]
        assert finder.__class__.__name__ == "_IsolatedImportFinder"

    def test_finder_intercepts_tox_imports(self) -> None:
        """Finder should handle tox imports."""
        import sys
        from toxology._stubs import install_import_hook

        install_import_hook()

        finder = sys.meta_path[0]

        # Should intercept these (only test modules that exist as files)
        assert finder.find_spec('tox', None) is not None
        assert finder.find_spec('virtualenv', None) is not None
        assert finder.find_spec('cachetools', None) is not None
        assert finder.find_spec('filelock', None) is not None

    def test_finder_ignores_other_imports(self) -> None:
        """Finder should not interfere with other imports."""
        import sys
        from toxology._stubs import install_import_hook

        install_import_hook()

        finder = sys.meta_path[0]

        # Should return None for these (not our concern)
        assert finder.find_spec('os', None) is None
        assert finder.find_spec('sys', None) is None
        assert finder.find_spec('packaging', None) is None
        assert finder.find_spec('pytest', None) is None

    def test_stubs_not_in_sys_modules_before_use(self) -> None:
        """Stubs should not pollute sys.modules until actually imported."""
        import sys

        # Clear any toxology and stub imports to get a fresh start
        to_remove = [m for m in sys.modules if 'toxology' in m or
                     any(stub in m for stub in ['virtualenv', 'cachetools',
                         'filelock', 'platformdirs', 'pyproject_api',
                         'distlib', 'python_discovery', 'tomli_w', 'colorama'])]
        for m in to_remove:
            del sys.modules[m]

        # Install import hook (but doesn't load stubs)
        from toxology._stubs import install_import_hook

        install_import_hook()

        # Stub modules should NOT be in sys.modules yet (not pre-populated)
        # They only get loaded when tox actually imports them
        assert 'cachetools' not in sys.modules
        assert 'filelock' not in sys.modules

    def test_stub_modules_work_when_imported(self, tox_project_toml: Path) -> None:
        """Stub modules should work correctly when imported by tox."""
        from toxology import read_tox_config

        # This will cause tox to import our stubs
        config = read_tox_config("py312", path=tox_project_toml)
        assert config.name == "py312"

        # Now stubs should be in sys.modules (because tox imported them)
        import virtualenv  # ty: ignore[unresolved-import]

        assert virtualenv.__version__ == "0.0.0"  # Our stub


