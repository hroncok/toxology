"""Stub for pyproject-api - only used for PEP 517 builds."""

from __future__ import annotations


class BackendFailed(Exception):
    """Stub exception."""

    pass


class Frontend:
    """Stub frontend."""

    backend = "setuptools"  # Stub backend name

    @staticmethod
    def create_args_from_folder(*args: object, **kwargs: object) -> tuple:
        """Stub method."""
        return ()

    def get_requires_for_build_editable(self, *args: object, **kwargs: object) -> list:
        """Stub method."""
        return []

    def get_requires_for_build_wheel(self, *args: object, **kwargs: object) -> list:
        """Stub method."""
        return []

    def get_requires_for_build_sdist(self, *args: object, **kwargs: object) -> list:
        """Stub method."""
        return []

    def prepare_metadata_for_build_editable(self, *args: object, **kwargs: object) -> None:
        """Stub method."""
        return None

    def prepare_metadata_for_build_wheel(self, *args: object, **kwargs: object) -> None:
        """Stub method."""
        return None

    def build_editable(self, *args: object, **kwargs: object) -> str:
        """Stub method."""
        return ""

    def build_wheel(self, *args: object, **kwargs: object) -> str:
        """Stub method."""
        return ""

    def build_sdist(self, *args: object, **kwargs: object) -> str:
        """Stub method."""
        return ""


class SubprocessFrontend:
    """Stub subprocess frontend."""

    pass


class CmdStatus:
    """Stub command status."""

    pass


class MetadataForBuildEditableResult:
    """Stub metadata result."""

    pass


class MetadataForBuildWheelResult:
    """Stub metadata result."""

    pass
