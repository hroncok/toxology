"""Tests for import isolation via MetaPathFinder."""

import sys
from pathlib import Path


from toxology import read_tox_config
from toxology._stubs import install_import_hook


class TestImportIsolation:
    """Test that MetaPathFinder provides proper import isolation."""

    def test_finder_installed_in_meta_path(self) -> None:
        """Ensure our finder is installed in sys.meta_path."""
        install_import_hook()

        # Finder should be first in meta_path
        finder = sys.meta_path[0]
        assert finder.__class__.__name__ == "_IsolatedImportFinder"

    def test_finder_intercepts_tox_imports(self) -> None:
        """Finder should handle tox imports."""
        install_import_hook()

        finder = sys.meta_path[0]

        # Should intercept these (only test modules that exist as files)
        assert finder.find_spec('tox', None) is not None
        assert finder.find_spec('virtualenv', None) is not None
        assert finder.find_spec('cachetools', None) is not None
        assert finder.find_spec('filelock', None) is not None

    def test_finder_ignores_other_imports(self) -> None:
        """Finder should not interfere with other imports."""
        install_import_hook()

        finder = sys.meta_path[0]

        # Should return None for these (not our concern)
        assert finder.find_spec('os', None) is None
        assert finder.find_spec('sys', None) is None
        assert finder.find_spec('packaging', None) is None
        assert finder.find_spec('pytest', None) is None

    def test_stubs_not_in_sys_modules_before_use(self) -> None:
        """Stubs should not pollute sys.modules until actually imported."""
        # Clear any toxology and stub imports to get a fresh start
        to_remove = [m for m in sys.modules if 'toxology' in m or
                     any(stub in m for stub in ['virtualenv', 'cachetools',
                         'filelock', 'platformdirs', 'pyproject_api',
                         'distlib', 'python_discovery', 'tomli_w', 'colorama'])]
        for m in to_remove:
            del sys.modules[m]

        # Install import hook (but doesn't load stubs)
        install_import_hook()

        # Stub modules should NOT be in sys.modules yet (not pre-populated)
        # They only get loaded when tox actually imports them
        assert 'cachetools' not in sys.modules
        assert 'filelock' not in sys.modules

    def test_stub_modules_work_when_imported(self, tox_project_toml: Path) -> None:
        """Stub modules should work correctly when imported by tox."""
        # This will cause tox to import our stubs
        config = read_tox_config("py312", path=tox_project_toml)
        assert config.name == "py312"

        # Now stubs should be in sys.modules (because tox imported them)
        import virtualenv  # ty: ignore[unresolved-import]

        assert virtualenv.__version__ == "0.0.0"  # Our stub
