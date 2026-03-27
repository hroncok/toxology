"""Import isolation for vendored tox and stubbed dependencies.

This module provides a MetaPathFinder that:
- Redirects tox imports to vendored tox code in _vendored/tox/
- Redirects stub module imports to stub implementations in _stubs/
- Allows user code to import real packages without seeing our stubs
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


# Install the finder at the front of sys.meta_path
_vendored_dir = Path(__file__).parent.parent / "_vendored"
_stubs_dir = Path(__file__).parent
_finder = _IsolatedImportFinder(
    vendored_path=str(_vendored_dir),
    stubs_path=str(_stubs_dir),
    stub_modules=_STUB_MODULES,
)

# Only install if not already present (avoid duplicates)
if not any(
    isinstance(finder, _IsolatedImportFinder) for finder in sys.meta_path
):
    sys.meta_path.insert(0, _finder)
