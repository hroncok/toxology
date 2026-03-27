"""Stub for platformdirs - only used for finding user config."""

from __future__ import annotations

from pathlib import Path


def user_config_dir(*args: object, **kwargs: object) -> str:
    """Return user config dir - uses real home directory."""
    return str(Path.home() / ".config")


def user_cache_dir(*args: object, **kwargs: object) -> str:
    """Return user cache dir - uses real home directory."""
    return str(Path.home() / ".cache")


def user_data_dir(*args: object, **kwargs: object) -> str:
    """Return user data dir - uses real home directory."""
    return str(Path.home() / ".local" / "share")
