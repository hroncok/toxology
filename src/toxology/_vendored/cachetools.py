"""Stub for cachetools - only used in virtualenv package building."""

from __future__ import annotations


def cached(*args: object, **kwargs: object) -> object:
    """No-op cached decorator - returns the function unchanged."""
    # If called with a function directly, return it
    if len(args) == 1 and callable(args[0]):
        return args[0]
    # If called with arguments, return a decorator
    def decorator(func: object) -> object:
        return func

    return decorator
