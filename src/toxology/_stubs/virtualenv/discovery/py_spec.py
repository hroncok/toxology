"""Stub for virtualenv.discovery.py_spec module."""

from __future__ import annotations

import platform
import sys


class PythonSpec:
    """Stub PythonSpec class with necessary attributes."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self.str_spec = ""
        self.implementation = "CPython"
        self.architecture = 64 if sys.maxsize > 2**32 else 32
        self.version_info = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        self.major = sys.version_info.major
        self.minor = sys.version_info.minor
        self.micro = sys.version_info.micro
        self.machine = platform.machine()
        self.free_threaded = getattr(sys, "_is_gil_enabled", lambda: False)() if hasattr(sys, "_is_gil_enabled") else False

    @classmethod
    def from_string_spec(cls, spec: str) -> PythonSpec:
        """Stub method that returns a PythonSpec instance."""
        # Return None path for version specs, actual path for python executables
        return cls(path=None)
