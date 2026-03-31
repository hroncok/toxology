# toxology

Read tox configuration (deps, extras, dependency groups, commands, setenv, changedir) using the tox Python API **without requiring tox as a runtime dependency**.

Toxology vendors tox and provides lightweight stubs for its dependencies, making it suitable for use in Fedora/RHEL RPM builds where tox and virtualenv are not available.

## ⚠️ Project Status: Proof of Concept

**This is an experimental proof of concept project created with extensive AI assistance to explore whether this vendoring approach is viable.**

- ⚠️ **API is unstable** - The API may change at any time without notice
- ⚠️ **Not production-ready** - This is for experimentation only
- ⚠️ **Uncertain future** - It is not yet determined whether this will be used in Fedora RPM macros or continue development

**Do not use this project for anything beyond experimentation and evaluation.**

## Features

- ✅ **No tox runtime dependency** - tox is vendored, only `packaging>=26` and `pluggy` required
- ✅ **Comprehensive config extraction** - deps, extras, dependency_groups, commands, setenv, changedir
- ✅ **All tox config formats** - tox.ini, pyproject.toml, setup.cfg
- ✅ **Full tox features** - factor expansion, placeholders, conditional deps, markers
- ✅ **95.3% success rate** on real-world Fedora packages (205/215) - the rest appear to be broken configs anyway
- ✅ **Python 3.12+** support

## Installation

```bash
pip install toxology
```

**Runtime dependencies**: Only `packaging>=26` and `pluggy` (both available in Fedora ELN).

## API Reference

### `read_tox_config(env: str, path: Path | None = None) -> ToxEnvConfig`

Read tox configuration for a given environment.

**Parameters:**
- `env` (str): Environment name (e.g., `"py312"`, `"lint"`)
- `path` (Path | None): Project root or config file location. Defaults to current directory.

**Returns:** `ToxEnvConfig` with the following attributes:
- `name` (str): Environment name
- `deps` (tuple[str, ...]): Dependency specifiers as tox would pass to pip
- `extras` (frozenset[str]): Extras to install for the target package
- `dependency_groups` (frozenset[str]): Dependency groups to install
- `commands` (tuple[Command, ...]): Test commands with `.args`, `.ignore_exit_code`, `.invert_exit_code`
- `setenv` (dict[str, str]): Environment variables to set when running commands
- `changedir` (Path | None): Working directory for commands

**Convenience properties:**
- `deps_list` → `list[str]`
- `extras_set` → `set[str]`
- `dependency_groups_set` → `set[str]`
- `commands_list` → `list[Command]`

## Example usage

Given a tox configuration like this:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"

[tool.tox]
env_list = ["py312", "lint"]

[tool.tox.env.py312]
deps = ["pytest>=8"]
extras = ["dev"]
dependency_groups = ["test"]
commands = [["pytest", "tests"], ["coverage", "report"]]

[tool.tox.env.lint]
deps = ["ruff"]
commands = [["ruff", "check", "."]]
```

This is what the library returns:

```python
from toxology import read_tox_config

config = read_tox_config("py312")  # path= defaults to current directory
assert config.name == "py312"
assert config.deps == ("pytest>=8",)
assert config.extras == frozenset({"dev"})
assert config.dependency_groups == frozenset({"test"})
assert tuple(config.commands[0].args) == ("pytest", "tests")
assert tuple(config.commands[1].args) == ("coverage", "report")

configs = {env: read_tox_config(env) for env in ["py312", "lint"]}
assert configs["lint"].name == "lint"
assert tuple(configs["lint"].commands[0].args) == ("ruff", "check", ".")
```

## Supported tox Features

Toxology correctly handles:

- **Factor expansion**: `py{38,39,310}` → `py38`, `py39`, `py310`
- **Placeholders**: `{envpython}`, `{envtmpdir}`, `{toxinidir}` resolved to `sys.prefix` paths
- **Conditional dependencies**: `mock; python_version < "3.3"`
- **PEP 508 markers**: `pytest>=8; sys_platform == "linux"`
- **Substitutions**: `{toxinidir}/data`, `{env:HOME}`
- **Complex setenv**: Multi-line, markers, file references
- **All config formats**: `tox.ini`, `pyproject.toml`, `setup.cfg`

## Vendoring Approach

Toxology uses a unique vendoring strategy to eliminate tox as a runtime dependency:

### What's Vendored
- **tox** only (~150 files, ~80KB)

### What's Stubbed (Not Vendored)
Instead of vendoring tox's dependencies, we provide lightweight stubs:
- `virtualenv`, `distlib`, `python-discovery` - Not needed for config reading
- `cachetools`, `filelock` - Only used in package building
- `platformdirs` - Only for user config (we use project config)
- `pyproject-api`, `tomli-w`, `colorama` - Not needed for our use case

### Runtime Dependencies
Only **2 packages** from Fedora ELN:
- `packaging>=26` - Essential for parsing deps/requirements/markers
- `pluggy` - Plugin system infrastructure

See [VENDORING.md](VENDORING.md) for details on how to update vendored tox.

## Real-World Validation

Tested on **215 real Fedora packages**:
- ✅ **205/215 succeeded (95.3%)**
- ✅ All 10 failures were legitimate package issues (missing tox configs or broken tox.ini files)
- ✅ Successfully extracts config from pytest, OpenStack, Fedora tooling packages

## Use Cases

### Fedora/RHEL RPM Builds
Primary use case: Replace `tox-current-env` in the `%tox` RPM macro to run tests without requiring tox/virtualenv in RHEL.

### CI/CD Systems
Extract tox configuration to generate test matrices or validate tox configs without installing tox.

### Build Tools
Read tox deps/extras to populate other build system configurations.

## Development

Run all checks (tests, type checking, lint) with tox:

```bash
tox
```

Run a single environment, e.g. tests on one Python version or just lint:

```bash
tox run -e py312
tox run -e lint
tox run -e typing
```

## Compatibility

- **Tox version**: 4 (vendored, for exact version see src/toxology/_vendored/vendor.txt)
- **Python versions**: 3.12, 3.13, 3.14+
- **Config formats**: tox.ini, pyproject.toml, setup.cfg
- **Tox features**: Factor expansion, placeholders, conditional deps, markers, setenv, changedir

## Limitations

Toxology is designed for **config reading only**. It does not:
- ❌ Create or manage virtual environments
- ❌ Install packages
- ❌ Run test commands
- ❌ Build wheels or sdists

These limitations are intentional - toxology extracts configuration so other tools (like RPM macros) can use it.

## License

MIT License - see LICENSE file for details.

Vendored tox is distributed under its original MIT license.
