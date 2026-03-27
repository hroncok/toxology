"""Stub for filelock - only used for virtualenv locking."""

from __future__ import annotations


class FileLock:
    """No-op file lock context manager."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.is_locked = False  # Always report as unlocked

    def acquire(self, *args: object, **kwargs: object) -> None:
        """No-op acquire."""
        pass

    def release(self, *args: object, **kwargs: object) -> None:
        """No-op release."""
        pass

    def __enter__(self) -> FileLock:
        return self

    def __exit__(self, *args: object) -> None:
        pass
