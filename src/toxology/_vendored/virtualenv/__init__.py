"""Stub for virtualenv package - not needed for config reading."""

from pathlib import Path

from toxology._vendored._stubs import StubVirtualenv

_module = StubVirtualenv()
__version__ = _module.__version__
app_data = _module.app_data
session_via_cli = _module.session_via_cli
Creator = _module.Creator
Session = _module.Session
__path__ = [str(Path(__file__).parent)]  # Makes it a package with submodules
