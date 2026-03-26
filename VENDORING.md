# Vendoring Documentation

## Why We Vendor

Toxology vendors tox to eliminate it as a runtime dependency for Fedora/RHEL RPM builds. This allows the `%tox` RPM macro to work without requiring tox and its heavy dependency chain (especially virtualenv) to be packaged in RHEL.

## What's Vendored

We vendor **only tox itself** (~150 files, ~80KB):
- Located in `src/toxology/_vendored/tox/`

## What's Stubbed (Not Vendored)

Instead of vendoring tox's dependencies, we provide lightweight stubs:

- **virtualenv** - Not needed for config reading; stub provides paths under `sys.prefix`
- **distlib** - virtualenv dependency
- **python-discovery** - virtualenv dependency
- **cachetools** - Only used in virtualenv package building
- **filelock** - Only used for virtualenv locking
- **platformdirs** - Only used for finding user config (we use project config)
- **pyproject-api** - Only used for PEP 517 builds
- **tomli-w** - Not used by tox at all
- **colorama** - Only for terminal colors (display only)

Stubs are located in `src/toxology/_vendored/_stubs.py` and installed into `sys.modules` before vendored tox is imported.

## Runtime Dependencies (available in Fedora ELN)

Only **2 packages** are required at runtime:

- **packaging>=26** - Essential for parsing deps/requirements/markers/versions (includes packaging.pylock)
- **pluggy** - Plugin system infrastructure (small, easier to keep than stub)

## Patches Applied to Vendored Code

We apply minimal patches to vendored tox via `tox.patch`.

## How to Update Vendored Tox

### Update to Latest Version

```bash
python vendor.py
```

This will:
1. Query PyPI for the latest tox version
2. Download it using pip
3. Extract to `src/toxology/_vendored/tox/`
4. Apply patches from `tox.patch` using `patch` command
5. Update `vendor.txt` with the new version and date

### Update to Specific Version

```bash
python vendor.py --version 4.24.0
```

### After Updating

1. **Run tests** to ensure patches applied cleanly:
   ```bash
   tox run -e py312,py313,py314
   ```

2. **Test on real packages** to verify compatibility:
   ```bash
   .venv/bin/python3 run_fedpkg_inspect.py
   ```

3. **Review changes** in vendored code:
   ```bash
   git diff src/toxology/_vendored/
   ```

### If Patches Fail to Apply

When upgrading to a newer tox version, patches may fail if tox changed the files we patch:

1. **Manually apply changes** to `src/toxology/_vendored/tox/`:
   - Edit `plugin/manager.py`: Make `_load_external_plugins()` just `pass`
   - Edit `config/sets.py`: Make `_on_duplicate_conf()` just `pass`
   - Add `# TOXOLOGY:` comments to mark the changes

2. **Regenerate the patch file**:
   ```bash
   git add src/toxology/_vendored/tox
   git diff --cached src/toxology/_vendored/tox/plugin/manager.py src/toxology/_vendored/tox/config/sets.py > tox.patch
   git reset HEAD src/toxology/_vendored/tox
   ```

3. **Test** that the new patch works:
   ```bash
   rm -rf src/toxology/_vendored/tox
   python vendor.py --version <version>
   tox run -e py312
   ```

## Vendoring Strategy

Our approach minimizes vendored code:

- ✅ Vendor **only tox** (~80KB)
- ✅ Stub **8 packages** instead of vendoring them (saves ~2MB+)
- ✅ Keep **2 packages** available in Fedora ELN (packaging, pluggy)
- ✅ **2 files patched** in vendored tox (minimal maintenance)

This results in:
- Small vendored footprint
- Minimal maintenance burden
- Easy updates to new tox versions
- Works on 95.3% of real-world Fedora packages

## Stub System Architecture

The stub system works by intercepting imports **before** vendored tox is loaded:

1. `from toxology import _vendored` runs first
2. Stubs are installed into `sys.modules`
3. Vendored path is added to `sys.path`
4. When tox imports virtualenv/cachetools/etc., it gets our stubs
5. Stubs provide minimal interfaces that tox needs for config reading

Example stub structure:

```python
class StubVirtualenv(ModuleType):
    class Creator:
        def __init__(self):
            import sys
            self.exe = Path(sys.executable)
            self.interpreter = InterpreterStub()

    class Session:
        def __init__(self):
            self.creator = StubVirtualenv.Creator()
```

This allows tox's placeholder resolution (`{envpython}`, `{envtmpdir}`) to work naturally, resolving to `sys.prefix` paths instead of creating real virtualenvs.

## Version Compatibility

Toxology is tested with:
- **Tox version**: 4.50.3 (latest as of vendoring)
- **Python versions**: 3.12, 3.13, 3.14
- **Tox config formats**: tox.ini, pyproject.toml, setup.cfg


## Troubleshooting

### Import errors from stubbed packages

If you see errors like `AttributeError: 'StubXYZ' object has no attribute 'foo'`:

1. Check which stubbed package is missing the attribute
2. Add the attribute to the stub class in `_stubs.py`
3. Run tests to verify the fix

### Patch application failures

If `vendor.py` reports patch failures:

1. Check if tox refactored the patched files
2. Manually update patches in `vendor.py`
3. Consider if the patch is still needed

### Config extraction errors

If `read_tox_config()` fails on a previously working package:

1. Test with upstream tox to see if it's a tox regression
2. Check if new tox version uses features we stub
3. Update stubs as needed

## License Compliance

Vendored tox is distributed under its original MIT license. The license file is copied to `src/toxology/_vendored/tox/LICENSE` during vendoring.
