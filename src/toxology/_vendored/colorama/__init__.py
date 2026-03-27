"""Stub for colorama - only for terminal colors (display only)."""

from pathlib import Path

__path__ = [str(Path(__file__).parent)]


def init(*args: object, **kwargs: object) -> None:
    """No-op init function."""
    pass


class Fore:
    """Color codes - all empty strings since we don't need colors."""

    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""
    LIGHTBLACK_EX = ""
    LIGHTRED_EX = ""
    LIGHTGREEN_EX = ""
    LIGHTYELLOW_EX = ""
    LIGHTBLUE_EX = ""
    LIGHTMAGENTA_EX = ""
    LIGHTCYAN_EX = ""
    LIGHTWHITE_EX = ""


class Back:
    """Background color codes - all empty strings."""

    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""


class Style:
    """Style codes - all empty strings."""

    DIM = ""
    NORMAL = ""
    BRIGHT = ""
    RESET_ALL = ""
