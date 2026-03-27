"""Import isolation for vendored tox and stubbed dependencies.

This module provides a MetaPathFinder that:
- Redirects tox imports to vendored tox code in _vendored/tox/
- Redirects stub module imports to stub implementations in _stubs/
- Allows user code to import real packages without seeing our stubs

To use the import hook, call install_import_hook() before importing tox.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Stub modules that we provide instead of vendoring
_STUB_MODULES = {
    "virtualenv",
    "cachetools",
    "filelock",
    "platformdirs",
    "pyproject_api",
    "distlib",
    "python_discovery",
    "tomli_w",
    "colorama",
}


class _IsolatedImportFinder:
    """MetaPathFinder to isolate vendored tox and stub module imports.

    This finder sits at the front of sys.meta_path and intercepts:
    - tox.* imports → redirects to _vendored/tox/
    - stub module imports → redirects to _stubs/

    All other imports return None, letting the standard import system handle them.
    """

    def __init__(self, vendored_path: str, stubs_path: str, stub_modules: set[str]) -> None:
        self.vendored_path = vendored_path  # Path to vendored tox code
        self.stubs_path = stubs_path  # Path to stub implementations
        self.stub_modules = stub_modules
        # Extract top-level package names for quick lookup
        self.stub_packages = {name.split(".")[0] for name in stub_modules}

    def find_spec(
        self,
        fullname: str,
        path: object,
        target: object = None,
    ) -> object | None:
        """Find module spec for tox or stub modules."""
        # Import PathFinder here to avoid namespace issues
        from importlib.machinery import PathFinder

        # Intercept tox imports and redirect to vendored code
        if fullname == "tox" or fullname.startswith("tox."):
            return PathFinder.find_spec(fullname, path=[self.vendored_path])

        # Intercept stub module imports and redirect to stubs
        top_level = fullname.split(".")[0]
        if top_level in self.stub_packages:
            return PathFinder.find_spec(fullname, path=[self.stubs_path])

        # Not our concern, let standard import system proceed
        return None


def install_import_hook() -> None:
    """Install import hook for vendored tox and stub modules.

    This function must be called before importing tox or using read_tox_config().
    It installs a custom MetaPathFinder that redirects tox imports to vendored
    code and stub module imports to our stub implementations.

    The function is idempotent - calling it multiple times is safe and will not
    install duplicate hooks.

    Example:
        from toxology._stubs import install_import_hook
        install_import_hook()
        from toxology import read_tox_config  # Now safe to import
    """
    # Check if already installed (idempotent)
    if any(isinstance(finder, _IsolatedImportFinder) for finder in sys.meta_path):
        return

    # Create and install finder
    vendored_dir = Path(__file__).parent.parent / "_vendored"
    stubs_dir = Path(__file__).parent
    finder = _IsolatedImportFinder(
        vendored_path=str(vendored_dir),
        stubs_path=str(stubs_dir),
        stub_modules=_STUB_MODULES,
    )
    sys.meta_path.insert(0, finder)
