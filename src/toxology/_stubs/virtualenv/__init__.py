"""Stub for virtualenv package - not needed for config reading."""

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.0.0"
__path__ = [str(Path(__file__).parent)]


class Creator:
    """Stub virtualenv Creator that provides paths under sys.prefix."""

    def __init__(self) -> None:
        self.exe = Path(sys.executable)
        self.script_dir = Path(sys.prefix) / "bin"
        self.purelib = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        self.platlib = self.purelib
        self.libs = [self.purelib]
        self.interpreter = self._create_interpreter_stub()

    def _create_interpreter_stub(self) -> InterpreterStub:
        """Create a stub interpreter object."""
        return InterpreterStub()

    @property
    def env_dir(self) -> Path:
        """Return sys.prefix as the env dir."""
        return Path(sys.prefix)


class InterpreterStub:
    """Stub for virtualenv interpreter."""

    def __init__(self) -> None:
        import platform as platform_module

        self.version_info = sys.version_info
        self.version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.platform = sys.platform
        self.implementation = "CPython"
        self.system_executable = Path(sys.executable)
        self.architecture = 64  # Assume 64-bit
        self.is_64 = True
        self.machine = platform_module.machine()
        self.free_threaded = getattr(sys, "_is_gil_enabled", lambda: False)() if hasattr(sys, "_is_gil_enabled") else False


class Session:
    """Stub virtualenv session."""

    def __init__(self) -> None:
        self.creator = Creator()


def app_data(*args: object, **kwargs: object) -> object:
    """Stub app_data function."""
    return object()


def session_via_cli(*args: object, **kwargs: object) -> Session:
    """Stub session_via_cli function that returns a session with creator."""
    return Session()
