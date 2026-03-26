"""Vendored dependencies with import isolation using MetaPathFinder.

This module installs a custom MetaPathFinder that isolates vendored tox imports.
The finder ensures:
- User code can import real packages without getting our stubs
- Vendored tox code gets our stubs when it imports these packages
- No pollution of global sys.modules or sys.path

The finder intercepts imports of tox.* and stubbed modules, redirecting them
to our _vendored/ directory while letting all other imports proceed normally.
"""

from __future__ import annotations

import sys
from importlib.machinery import PathFinder
from pathlib import Path

# Define which modules should be stubbed
_STUB_MODULES = {
    'virtualenv',
    'cachetools',
    'filelock',
    'platformdirs',
    'pyproject_api',
    'distlib',
    'python_discovery',
    'tomli_w',
    'colorama',
}


class _VendoredImportFinder:
    """MetaPathFinder to isolate vendored tox and stub module imports.

    This finder intercepts imports of:
    1. The vendored tox package (tox.*)
    2. Stub modules (virtualenv, cachetools, filelock, etc.)

    It redirects these imports to our _vendored/ directory while allowing
    all other imports to proceed normally through the standard import system.
    """

    def __init__(self, vendored_path: str, stub_modules: set[str]):
        """Initialize the finder.

        Args:
            vendored_path: Absolute path to the _vendored directory
            stub_modules: Set of module names that should use stubs
        """
        self.vendored_path = vendored_path
        self.stub_modules = stub_modules
        # Pre-compute top-level package names for efficient lookup
        self.stub_packages = {name.split('.')[0] for name in stub_modules}

    def find_spec(self, fullname: str, path: object, target: object = None) -> object | None:
        """Find module spec for vendored/stubbed imports.

        Args:
            fullname: Fully qualified module name
            path: Package path (unused)
            target: Target module (unused)

        Returns:
            ModuleSpec if this finder should handle the import, None otherwise
        """
        from importlib.machinery import PathFinder

        # Intercept tox imports
        if fullname == 'tox' or fullname.startswith('tox.'):
            return PathFinder.find_spec(fullname, path=[self.vendored_path])

        # Intercept stub module imports
        top_level = fullname.split('.')[0]
        if top_level in self.stub_packages:
            return PathFinder.find_spec(fullname, path=[self.vendored_path])

        # Not our concern, let standard import proceed
        return None


# Install the finder at the front of sys.meta_path
# This must happen BEFORE any imports of tox or stubbed modules
_VENDORED_PATH = str(Path(__file__).parent)
_finder = _VendoredImportFinder(_VENDORED_PATH, _STUB_MODULES)

# Only install if not already present (avoid double installation)
if _finder not in sys.meta_path:
    sys.meta_path.insert(0, _finder)

# Clean up namespace
del Path, PathFinder
