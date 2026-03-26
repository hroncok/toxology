"""Vendored dependencies with stubs for unneeded packages.

This module:
1. Installs stub modules into sys.modules (BEFORE vendored tox is imported)
2. Adds the vendored directory to sys.path

The stubs intercept imports from vendored tox, preventing it from importing
packages we don't need (virtualenv, cachetools, filelock, etc.).
"""

from __future__ import annotations

import sys
from pathlib import Path

from toxology._vendored._stubs import (
    StubCachetools,
    StubColorama,
    StubDistlib,
    StubFilelock,
    StubPlatformdirs,
    StubPythonDiscovery,
    StubPyprojectApi,
    StubTomliW,
    StubVirtualenv,
    StubVirtualenvDiscovery,
    StubVirtualenvDiscoveryPySpec,
)

# Install stubs BEFORE adding vendored path to sys.path
# This ensures tox imports our stubs instead of trying to import real packages
virtualenv_stub = StubVirtualenv()
virtualenv_stub.__version__ = "0.0.0"  # type: ignore[attr-defined]
virtualenv_stub.app_data = StubVirtualenv.app_data  # type: ignore[attr-defined]
virtualenv_stub.session_via_cli = StubVirtualenv.session_via_cli  # type: ignore[attr-defined]
sys.modules["virtualenv"] = virtualenv_stub

# Set up virtualenv submodules
virtualenv_discovery_stub = StubVirtualenvDiscovery()
sys.modules["virtualenv.discovery"] = virtualenv_discovery_stub

virtualenv_discovery_py_spec_stub = StubVirtualenvDiscoveryPySpec()
sys.modules["virtualenv.discovery.py_spec"] = virtualenv_discovery_py_spec_stub
virtualenv_discovery_py_spec_stub.PythonSpec = StubVirtualenvDiscoveryPySpec.PythonSpec  # type: ignore[attr-defined]
sys.modules["distlib"] = StubDistlib("distlib")
sys.modules["python_discovery"] = StubPythonDiscovery("python_discovery")

cachetools_stub = StubCachetools()
sys.modules["cachetools"] = cachetools_stub
cachetools_stub.cached = StubCachetools.cached  # type: ignore[attr-defined]

filelock_stub = StubFilelock()
sys.modules["filelock"] = filelock_stub
# filelock.FileLock needs to be accessible
filelock_stub.FileLock = StubFilelock.FileLock  # type: ignore[attr-defined]

platformdirs_stub = StubPlatformdirs()
sys.modules["platformdirs"] = platformdirs_stub

pyproject_api_stub = StubPyprojectApi()
sys.modules["pyproject_api"] = pyproject_api_stub
# pyproject_api exceptions/classes need to be accessible
pyproject_api_stub.BackendFailed = StubPyprojectApi.BackendFailed  # type: ignore[attr-defined]
pyproject_api_stub.Frontend = StubPyprojectApi.Frontend  # type: ignore[attr-defined]
pyproject_api_stub.SubprocessFrontend = StubPyprojectApi.SubprocessFrontend  # type: ignore[attr-defined]
pyproject_api_stub.CmdStatus = StubPyprojectApi.CmdStatus  # type: ignore[attr-defined]
pyproject_api_stub.MetadataForBuildEditableResult = StubPyprojectApi.MetadataForBuildEditableResult  # type: ignore[attr-defined]
pyproject_api_stub.MetadataForBuildWheelResult = StubPyprojectApi.MetadataForBuildWheelResult  # type: ignore[attr-defined]
sys.modules["tomli_w"] = StubTomliW("tomli_w")

colorama_stub = StubColorama()
sys.modules["colorama"] = colorama_stub
# colorama.Fore, .Back, .Style, init need to be accessible
colorama_stub.Fore = StubColorama.Fore  # type: ignore[attr-defined]
colorama_stub.Back = StubColorama.Back  # type: ignore[attr-defined]
colorama_stub.Style = StubColorama.Style  # type: ignore[attr-defined]
colorama_stub.init = StubColorama.init  # type: ignore[attr-defined]

# Now add vendored tox to import path
_VENDOR_PATH = str(Path(__file__).parent)
if _VENDOR_PATH not in sys.path:
    sys.path.insert(0, _VENDOR_PATH)
