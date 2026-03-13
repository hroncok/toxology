"""Read tox configuration using the tox Python API."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    from tox.config.cli.parse import Options
    from tox.config.types import Command
    from tox.session.state import State

    T = TypeVar("T")

@dataclass(frozen=True)
class ToxEnvConfig:
    """
    Resolved configuration for a single tox environment, as tox would use it.

    Attributes are the same concepts tox uses: dependencies, extras, and test commands.
    """

    name: str
    """Tox environment name (e.g. ``py312``, ``lint``)."""
    deps: tuple[str, ...]
    """Dependency specifiers as tox would pass to pip (after resolving factors, etc.)."""
    extras: frozenset[str]
    """Extras to install for the target package (normalized names)."""
    dependency_groups: frozenset[str]
    """Dependency groups to install for the target package (normalized names)."""
    commands: tuple[Command, ...]
    """Test commands (pre + main + post) as tox would execute them. Raw :class:`tox.config.types.Command` (``.args``, ``ignore_exit_code``, ``invert_exit_code``)."""

    @property
    def deps_list(self) -> list[str]:
        """Dependencies as a list (convenience)."""
        return list(self.deps)

    @property
    def extras_set(self) -> set[str]:
        """Extras as a set (convenience)."""
        return set(self.extras)

    @property
    def dependency_groups_set(self) -> set[str]:
        """Dependency groups as a set (convenience)."""
        return set(self.dependency_groups)

    @property
    def commands_list(self) -> list[Command]:
        """Commands as a list (convenience)."""
        return list(self.commands)


def read_tox_config(env: str, path: Path | None = None) -> ToxEnvConfig:
    """
    Read tox configuration for the given environment using the tox Python API.

    Resolves the same deps, extras, and commands that tox would use when running
    the environment, including factor resolution and inheritance.

    For multiple environments, call in a loop: ``[read_tox_config(e, path) for e in envs]``.

    :param env: Environment name (e.g. ``"py312"``, ``"lint"``).
    :param path: Project root or config file location. Defaults to current directory.
    :return: Resolved :class:`ToxEnvConfig` for the environment.
    :raises Exception: Re-raises errors from tox (e.g. missing config, invalid env name).
    """
    path = path or Path(".")
    path = path.resolve()

    options, args = _get_tox_options(path, env)
    state = _get_tox_state(options, args)
    tox_env = state.envs[env]
    conf = tox_env.conf
    deps_conf = conf["deps"]
    # unroll() -> (pip_options, dep_specifiers); we only need the dep strings
    _, deps_list = deps_conf.unroll()
    extras_set = _get_conf(conf, "extras", frozenset[str]())
    dependency_groups_set = _get_conf(conf, "dependency_groups", frozenset[str]())
    commands_pre = conf["commands_pre"]
    commands_main = conf["commands"]
    commands_post = conf["commands_post"]
    all_commands = (*commands_pre, *commands_main, *commands_post)

    return ToxEnvConfig(
        name=env,
        deps=tuple(deps_list),
        extras=frozenset(extras_set),
        dependency_groups=frozenset(dependency_groups_set),
        commands=all_commands,
    )


def _get_tox_options(path: Path, env: str) -> tuple[Options, list[str]]:
    from tox.config.cli.parse import get_options

    args = ["-c", str(path), "config", "-e", env]
    return get_options(*args), args


def _get_conf(conf: object, key: str, default: T) -> T:
    """Return conf[key], or default if key is missing."""
    try:
        return conf[key]  # type: ignore[index, return-value]
    except KeyError:
        return default


def _get_tox_state(options: Options, args: list[str]) -> State:
    from tox.session.state import State

    return State(options, args)
