"""Stub modules for dependencies not needed for config reading.

These stubs are installed into sys.modules before vendored tox is imported,
preventing tox from importing the real packages.
"""

from __future__ import annotations

from types import ModuleType


class StubVirtualenvDiscoveryPySpec(ModuleType):
    """Stub for virtualenv.discovery.py_spec module."""

    def __init__(self) -> None:
        super().__init__("virtualenv.discovery.py_spec")

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
        def from_string_spec(cls, spec: str) -> StubVirtualenvDiscoveryPySpec.PythonSpec:
            """Stub method that returns a PythonSpec instance."""
            # Return None path for version specs, actual path for python executables
            return cls(path=None)


class StubVirtualenvDiscovery(ModuleType):
    """Stub for virtualenv.discovery module."""

    def __init__(self) -> None:
        super().__init__("virtualenv.discovery")
        # Make this a package so submodules can be imported
        self.__path__ = []  # type: ignore[attr-defined]


class StubVirtualenv(ModuleType):
    """Stub for virtualenv - not needed for config reading."""

    __version__ = "0.0.0"  # Stub version

    def __init__(self) -> None:
        super().__init__("virtualenv")
        # Make this a package so submodules can be imported
        self.__path__ = []  # type: ignore[attr-defined]

    class Creator:
        """Stub virtualenv Creator that provides paths under sys.prefix."""

        def __init__(self) -> None:
            import sys
            from pathlib import Path

            self.exe = Path(sys.executable)
            self.script_dir = Path(sys.prefix) / "bin"
            self.purelib = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            self.platlib = self.purelib
            self.libs = [self.purelib]
            self.interpreter = self._create_interpreter_stub()

        def _create_interpreter_stub(self) -> object:
            """Create a stub interpreter object."""
            import sys
            from pathlib import Path

            class InterpreterStub:
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

            return InterpreterStub()

        @property
        def env_dir(self) -> object:
            """Return sys.prefix as the env dir."""
            import sys
            from pathlib import Path
            return Path(sys.prefix)

    class Session:
        """Stub virtualenv session."""

        def __init__(self) -> None:
            self.creator = StubVirtualenv.Creator()

    @staticmethod
    def app_data(*args: object, **kwargs: object) -> object:
        """Stub app_data function."""
        return object()

    @staticmethod
    def session_via_cli(*args: object, **kwargs: object) -> StubVirtualenv.Session:
        """Stub session_via_cli function that returns a session with creator."""
        return StubVirtualenv.Session()


class StubDistlib(ModuleType):
    """Stub for distlib - virtualenv dependency."""

    pass


class StubPythonDiscovery(ModuleType):
    """Stub for python-discovery - virtualenv dependency."""

    pass


class StubCachetools(ModuleType):
    """Stub for cachetools - only used in virtualenv package building."""

    def __init__(self) -> None:
        super().__init__("cachetools")

    @staticmethod
    def cached(*args: object, **kwargs: object) -> object:
        """No-op cached decorator - returns the function unchanged."""
        # If called with a function directly, return it
        if len(args) == 1 and callable(args[0]):
            return args[0]
        # If called with arguments, return a decorator
        def decorator(func: object) -> object:
            return func

        return decorator


class StubFilelock(ModuleType):
    """Stub for filelock - only used for virtualenv locking."""

    def __init__(self) -> None:
        super().__init__("filelock")

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

        def __enter__(self) -> StubFilelock.FileLock:
            return self

        def __exit__(self, *args: object) -> None:
            pass


class StubPlatformdirs(ModuleType):
    """Stub for platformdirs - only used for finding user config."""

    def __init__(self) -> None:
        super().__init__("platformdirs")

    @staticmethod
    def user_config_dir(*args: object, **kwargs: object) -> str:
        """Return user config dir - uses real home directory."""
        from pathlib import Path
        return str(Path.home() / ".config")

    @staticmethod
    def user_cache_dir(*args: object, **kwargs: object) -> str:
        """Return user cache dir - uses real home directory."""
        from pathlib import Path
        return str(Path.home() / ".cache")

    @staticmethod
    def user_data_dir(*args: object, **kwargs: object) -> str:
        """Return user data dir - uses real home directory."""
        from pathlib import Path
        return str(Path.home() / ".local" / "share")


class StubPyprojectApi(ModuleType):
    """Stub for pyproject-api - only used for PEP 517 builds."""

    def __init__(self) -> None:
        super().__init__("pyproject_api")

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


class StubTomliW(ModuleType):
    """Stub for tomli-w - not used by tox at all."""

    pass


class StubColorama(ModuleType):
    """Stub for colorama - only for terminal colors (display only)."""

    def __init__(self) -> None:
        super().__init__("colorama")

    @staticmethod
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
