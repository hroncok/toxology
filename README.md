# toxology

Read tox configuration (deps, extras, dependency groups, commands) using the tox Python API.

## Example usage

```python
from pathlib import Path
from toxology import read_tox_config

# Single environment
config = read_tox_config("py312")  # accepts path=, defaults to .
print(config.deps)  # tuple of dependency specifier strings
print(config.extras)  # frozenset of extra names
print(config.dependency_groups)  # frozenset of dependency group names
print(config.commands)  # tuple of ToxCommand (each has .args, .shell)

# Multiple environments: call in a loop
for env in ["py312", "lint"]:
    config = read_tox_config(env)
    print(f"{env}: {config.deps}, {[c.args for c in config.commands]}")
```

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
