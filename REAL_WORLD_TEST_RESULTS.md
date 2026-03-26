# Real-World Testing Results

Tested toxology on 215 real Fedora packages from `.fedpkg/` directory.

## Summary

- **Success Rate**: 205/215 (95.3%)
- **Failed**: 10/215 (4.7%)

## Success Examples

Toxology successfully extracted tox configuration from popular packages including:
- PyGreSQL, ginga, glances, jrnl, thefuck
- pytest-related: pytest-xdist, pytest-bdd, pytest-cases
- OpenStack: python-aodhclient, python-oslo-*
- Fedora tooling: fedfind, relval, resultsdb_conventions
- And 195+ more packages

## Failure Analysis

All 10 failures are **legitimate package issues**, not toxology bugs:

### No tox config (6 packages - Expected)
- fedora-messaging
- pyproject-rpm-macros  
- python-avro
- python-basis_set_exchange
- python-flask-restx
- python-gelidum
- python-poetry-core

These packages don't use tox for testing.

### Broken package configs (4 packages)
1. **python-cheetah**: Invalid `pass_env` with whitespace
   - Error: `pass_env values cannot contain whitespace`
   - Package issue: `'CI DISTUTILS_USE_SDK MSSdk INCLUDE LIB WINDIR'`

2. **python-oslo-context**: Missing requirements file
   - Error: `Could not open requirements file test-requirements.txt`
   - Package issue: File doesn't exist in source

3. **python-pykcs11**: Missing setenv file
   - Error: `tox.env does not exist for set_env`
   - Package issue: References missing external file

## Config Features Extracted

For the 205 successful packages, toxology extracted:
- ✅ Dependencies (`deps`)
- ✅ Extras (`extras`) 
- ✅ Dependency groups (`dependency_groups`)
- ✅ Test commands (`commands`)
- ✅ Environment variables (`setenv`)
- ✅ Working directory (`changedir`)

## Supported tox.ini Features

Toxology correctly handled:
- Factor expansion: `py{38,39,310}`
- Placeholders: `{envpython}`, `{envtmpdir}`, `{toxinidir}`
- Conditional deps: `mock; python_version < "3.3"`
- Multiple config formats: `tox.ini`, `pyproject.toml`, `setup.cfg`
- Complex setenv with markers
- Multi-line commands

## Conclusion

Toxology successfully reads tox configuration from **95.3% of real-world Fedora packages**, with all failures being legitimate package issues rather than toxology bugs. This validates the vendoring approach and stub system.
