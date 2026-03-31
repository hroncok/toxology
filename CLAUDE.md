# Instructions for Claude Code

This file contains instructions for Claude Code (AI assistant) when working on this project.

## Project Overview

Toxology is a focused library that reads tox configuration without requiring tox as a runtime dependency. It vendors tox and provides lightweight stubs for dependencies, making it suitable for Fedora/RHEL RPM builds.

**Core principle**: Keep it simple. The codebase is small (~777 lines) and should stay that way.

## Testing & Verification

### Always Use Installed Package

**CRITICAL**: Never run toxology code with `PYTHONPATH`. Always use a properly installed package.

```bash
# ✅ CORRECT - Use tox environments
tox -e py312
.tox/py312/bin/python script.py

# ✅ CORRECT - Install in editable mode (requires activated virtual environment)
pip install -e .
python script.py

# ❌ WRONG - Never use PYTHONPATH
PYTHONPATH=src python script.py  # This breaks import isolation!
```

**Why**: Toxology uses a MetaPathFinder import hook to isolate vendored tox and stubs. This requires proper package installation to work correctly.

### Verification Workflow

**Before committing ANY code changes**, always run:

```bash
# Run all tests on multiple Python versions, type checker and linter
tox

For fast feedback loop, you may also want to run just the Python tests for one Python version:

```
# Run only functional tests on Python 3.14
tox -e py314

# Run type checker
tox -e typing

# Run linter
tox -e lint
```

However before committing, all tox environments must pass. No exceptions.

**CRITICAL**: Running `tox` before every commit prevents:
- Syntax errors (e.g., invalid TOML structure)
- Type errors
- Test failures
- Broken commits that require amendments

If you modify vendoring:
```bash
# 4. Verify vendoring is reproducible
rm -rf src/toxology/_vendored/tox
python vendor.py --version 4.51.0
git diff src/toxology/_vendored/  # Should show no changes (except timestamps)
```

## Code Style

### Path Construction

Use single-string literals for consecutive path components:

```python
# ✅ CORRECT
path = Path(__file__).parent.parent / "src/toxology/_vendored/sbom.json"
VENDOR_DIR = REPO_ROOT / "src/toxology/_vendored"

# ❌ WRONG
path = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
```

Keep using `/` operator for variable joins:
```python
# ✅ CORRECT
sbom_path = VENDOR_DIR / "sbom.json"
```

### Simplicity

- Don't add features that aren't requested
- Don't add "improvements" or refactoring beyond the task
- Don't add error handling for scenarios that can't happen
- Don't create abstractions for one-time operations
- Trust that the code works - it has comprehensive tests

Example:
- A bug fix doesn't need surrounding code cleaned up
- A simple feature doesn't need extra configurability
- Don't add docstrings/comments to code you didn't change

## Commit Messages

Always use this format:

```
Short summary (imperative mood)

Detailed explanation of why.
Can be multiple paragraphs.

Assisted-By: Claude Sonnet 4.5
```

**Never** use `Co-Authored-By`. Always use `Assisted-By` without email address.

Do not repeat what changed in the commit message, unless it improves clarity.

```python
# ✅ CORRECT
Removed all generated files.

# ❌ WRONG
Removed results.json, status.txt and cache.db.
```


## What NOT to Do

### Don't Commit Generated Files

Never commit:
- Test results (`*_results.txt`, `*.log`)
- Build artifacts (`dist/`, `*.egg-info/`)
- Cache files (`.pytest_cache/`, `.ruff_cache/`)
- Virtual environments
- Test utilities meant for one-time use

Some are available in git history if needed.

### Don't Touch Vendored Code

Never edit files in `src/toxology/_vendored/tox/` directly.

If changes are needed:
1. Edit `tox.patch`
2. Run `python vendor.py --version <version>`
3. Verify with `git diff`

The only exception is when regenerating the patch after a tox version update.

### Don't Modify Import Isolation

The import hook in `src/toxology/_stubs/__init__.py` is critical. Don't modify it unless:
1. You fully understand MetaPathFinder and import hooks
2. You've tested extensively with real-world packages
3. The user explicitly requests changes

### Don't Mix Unrelated Changes

**CRITICAL**: Never mix unrelated changes in a single commit or action, even if you notice something is wrong.

**DO**:
- Make only the changes that were requested
- If you notice an unrelated issue, mention it separately to the user
- Let the user decide whether to address it

**DON'T**:
- Fix unrelated bugs or issues while working on a task
- Clean up unrelated code "while you're at it"
- Remove broken references or fix typos unless that's what was asked
- Remove or add blank lines that aren't part of the requested change
- Reformat existing text or code

Examples:
```
User: "Add warning section to README"

✅ CORRECT: Add only the warning section, mention broken reference separately
❌ WRONG: Add warning section AND fix broken reference in same change
```

```
User: "Add project.urls to pyproject.toml"

✅ CORRECT: Add [project.urls] section, keep all existing blank lines
❌ WRONG: Add [project.urls] AND remove blank line between classifiers and dependencies
```

If you notice something wrong, say: "I noticed X is broken. Should I fix that separately?"

After making changes, review `git diff` to ensure ONLY the requested changes are present.

## Vendoring

### Updating Vendored Tox

```bash
# Update to latest version
python vendor.py

# Update to specific version
python vendor.py --version 4.52.0

# Verify patches applied correctly
grep "# TOXOLOGY:" src/toxology/_vendored/tox/plugin/manager.py

# Run full test suite
tox
```

### If Patches Fail

When updating tox, patches may fail if tox changed the patched files:

1. Manually apply changes to `src/toxology/_vendored/tox/`
2. Add `# TOXOLOGY:` comment markers
3. Regenerate patch:
   ```bash
   git add src/toxology/_vendored/tox
   git diff --cached src/toxology/_vendored/tox/plugin/manager.py > tox.patch
   git reset HEAD src/toxology/_vendored/tox
   ```
4. Test that new patch works:
   ```bash
   rm -rf src/toxology/_vendored/tox
   python vendor.py --version <version>
   tox run -e py312
   ```

## Stubs

Stub modules in `src/toxology/_stubs/` provide minimal implementations of tox's dependencies.

**When to update stubs**:
- Tox version update breaks tests
- New tox features require additional stub attributes

**When updating stubs**:
- Use runtime values from `sys`, `platform`, etc. (not hardcoded values)
- Keep stubs minimal - only what tox actually uses
- Add comments explaining why each part exists
- Test with all Python versions

Example:
```python
# ✅ CORRECT - Runtime values
self.version_info = sys.version_info
self.architecture = 64 if sys.maxsize > 2**32 else 32

# ❌ WRONG - Hardcoded values
self.version_info = (3, 12, 0)
self.architecture = 64
```

## Documentation

### README.md
- User-facing documentation
- Keep it concise and practical
- API reference with examples
- Installation instructions

### VENDORING.md
- Technical documentation for maintainers
- How vendoring works
- How to update vendored tox
- Import isolation implementation details

### CLAUDE.md (this file)
- Instructions for Claude Code
- Development workflow
- Testing procedures
- Code style preferences

## Test Organization

Tests are organized by category:

- `tests/test_config.py` - Config extraction (core functionality)
- `tests/test_import_isolation.py` - Import hook isolation
- `tests/test_vendoring.py` - Vendoring verification
- `tests/conftest.py` - Shared fixtures

**Don't reorganize tests** unless explicitly requested.

**Don't add tests** for scenarios that:
- Are already covered by existing tests
- Test tox functionality (not toxology)
- Are implementation details, not behavior

## Common Tasks

### Adding New Config Field

1. Update `ToxEnvConfig` dataclass in `src/toxology/config.py`
2. Extract field in `read_tox_config()` function
3. Add property method if needed (e.g., `field_list`)
4. Add test in `tests/test_config.py`
5. Update README.md API reference
6. Run full test suite

### Updating to New Tox Version

1. Run `python vendor.py` (or specify version)
2. Check if patches applied: `git diff src/toxology/_vendored/`
3. If patches failed, manually apply and regenerate patch
4. Update SBOM (auto-generated by vendor.py)
5. Run full test suite
6. Commit with message mentioning tox version

### Fixing Type Errors

1. Never use private attributes (e.g., `dist._path`)
2. Use public APIs from importlib.metadata, pathlib, etc.
3. Add type ignore comments for vendored tox imports
4. Verify: `tox -e typing`

## Success Metrics

- ✅ All 51 tests pass on py312, py313, py314, py315
- ✅ Type checker passes (ty)
- ✅ Linter passes (ruff)
- ✅ 95.3% success rate on real-world Fedora packages
- ✅ Code stays simple and focused
- ✅ No regressions in vendoring reproducibility

## Questions?

If unsure about any change:
1. Check if tests cover the scenario
2. Look at existing code patterns
3. Ask the user before making significant changes
4. When in doubt, keep it simple
