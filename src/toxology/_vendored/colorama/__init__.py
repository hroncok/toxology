"""Stub for colorama - only for terminal colors (display only)."""

from pathlib import Path

from toxology._vendored._stubs import StubColorama

_module = StubColorama()
Fore = _module.Fore
Back = _module.Back
Style = _module.Style
init = _module.init
__path__ = [str(Path(__file__).parent)]
