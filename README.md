# toxology

Read tox configuration (deps, extras, dependency groups, commands) using the tox Python API.

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
assert tuple(c.args for c in config.commands) == (("pytest", "tests"), ("coverage", "report"))

configs = {env: read_tox_config(env) for env in ["py312", "lint"]}
assert configs["lint"].name == "lint"
assert configs["lint"].commands[0].args == ("ruff", "check", ".")
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
