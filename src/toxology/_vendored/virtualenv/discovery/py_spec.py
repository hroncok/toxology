"""Stub for virtualenv.discovery.py_spec module."""

from __future__ import annotations


class PythonSpec:
    """Stub PythonSpec class with necessary attributes."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self.str_spec = ""
        self.implementation = "CPython"
        self.architecture = 64
        self.version_info = (3, 12, 0)
        self.major = 3
        self.minor = 12
        self.micro = 0
        self.machine = "x86_64"
        self.free_threaded = False

    @classmethod
    def from_string_spec(cls, spec: str) -> PythonSpec:
        """Stub method that returns a PythonSpec instance."""
        # Return None path for version specs, actual path for python executables
        return cls(path=None)
