# Vendoring Documentation

## Why We Vendor

Toxology vendors tox to eliminate it as a runtime dependency for Fedora/RHEL RPM builds. This allows the `%tox` RPM macro to work without requiring tox and its heavy dependency chain (especially virtualenv) to be packaged in RHEL.

## What's Vendored

We vendor **only tox itself** (~150 files, ~80KB):
- Located in `src/toxology/_vendored/tox/`

## What's Stubbed (Not Vendored)

Instead of vendoring tox's dependencies, we provide lightweight stub modules that exist as real Python files in the `_vendored/` directory:

- **virtualenv** - Not needed for config reading; stub provides paths under `sys.prefix`
  - `_vendored/virtualenv/__init__.py` - Package stub
  - `_vendored/virtualenv/discovery/__init__.py` - Sub-package stub
  - `_vendored/virtualenv/discovery/py_spec.py` - Sub-module stub
- **distlib** - virtualenv dependency (`_vendored/distlib.py`)
- **python-discovery** - virtualenv dependency (`_vendored/python_discovery.py`)
- **cachetools** - Only used in virtualenv package building (`_vendored/cachetools.py`)
- **filelock** - Only used for virtualenv locking (`_vendored/filelock.py`)
- **platformdirs** - Only used for finding user config (`_vendored/platformdirs.py`)
- **pyproject-api** - Only used for PEP 517 builds (`_vendored/pyproject_api.py`)
- **tomli-w** - Not used by tox at all (`_vendored/tomli_w.py`)
- **colorama** - Only for terminal colors (`_vendored/colorama/__init__.py`)

Each stub module contains its implementation directly, with classes and functions defined at module level.

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
- ✅ Stub **9 packages** instead of vendoring them (saves ~2MB+)
- ✅ Keep **2 packages** available in Fedora ELN (packaging, pluggy)
- ✅ **2 files patched** in vendored tox (minimal maintenance)

This results in:
- Small vendored footprint
- Minimal maintenance burden
- Easy updates to new tox versions
- Works on 95.3% of real-world Fedora packages

## Import Isolation with MetaPathFinder

Toxology uses Python's `sys.meta_path` import hook system to achieve complete import isolation between vendored tox and user code.

### How It Works

1. When `toxology._vendored` is imported, a custom `MetaPathFinder` is installed at the front of `sys.meta_path`
2. When Python tries to import any module, it asks each finder in `sys.meta_path` (in order)
3. Our finder intercepts imports of `tox.*` and stubbed modules (virtualenv, cachetools, etc.)
4. These imports are redirected to the `_vendored/` directory using `PathFinder`
5. All other imports return `None`, letting the standard import system handle them

### Benefits

This approach ensures:
- **Vendored tox sees our stubs** when it imports virtualenv, cachetools, etc.
- **User code sees real packages** (or ImportError if not installed)
- **No global pollution** of `sys.modules` or `sys.path`
- **Import order independent** - Works regardless of whether you import toxology before or after other packages

### Implementation Details

**MetaPathFinder class** (`_vendored/__init__.py`):
```python
class _VendoredImportFinder:
    """MetaPathFinder to isolate vendored tox and stub module imports."""

    def find_spec(self, fullname: str, path: object, target: object = None):
        # Intercept tox imports
        if fullname == 'tox' or fullname.startswith('tox.'):
            return PathFinder.find_spec(fullname, path=[self.vendored_path])

        # Intercept stub module imports
        top_level = fullname.split('.')[0]
        if top_level in self.stub_packages:
            return PathFinder.find_spec(fullname, path=[self.vendored_path])

        # Not our concern, let standard import proceed
        return None
```

**Stub module structure**:

Stubs exist as real Python modules in the `_vendored/` directory:
- `_vendored/virtualenv/__init__.py` - Full package with `__path__` for submodules
- `_vendored/virtualenv/discovery/__init__.py` - Sub-package
- `_vendored/virtualenv/discovery/py_spec.py` - Sub-module
- `_vendored/cachetools.py` - Single-file stub
- (Similar for other stubbed packages)

Each stub module contains its implementation directly at module level. For example:

```python
# _vendored/virtualenv/__init__.py
from __future__ import annotations

import sys
from pathlib import Path

__version__ = "0.0.0"
__path__ = [str(Path(__file__).parent)]


class Creator:
    """Stub virtualenv Creator that provides paths under sys.prefix."""

    def __init__(self) -> None:
        self.exe = Path(sys.executable)
        self.script_dir = Path(sys.prefix) / "bin"
        self.purelib = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
        self.platlib = self.purelib
        self.libs = [self.purelib]
        self.interpreter = self._create_interpreter_stub()

    def _create_interpreter_stub(self) -> InterpreterStub:
        return InterpreterStub()


class Session:
    """Stub virtualenv session."""

    def __init__(self) -> None:
        self.creator = Creator()


def session_via_cli(*args: object, **kwargs: object) -> Session:
    """Stub session_via_cli function."""
    return Session()
```

This allows tox's placeholder resolution (`{envpython}`, `{envtmpdir}`) to work naturally, resolving to `sys.prefix` paths instead of creating real virtualenvs.

## Version Compatibility

Toxology is tested with:
- **Tox version**: 4.50.3 (latest as of vendoring)
- **Python versions**: 3.12, 3.13, 3.14
- **Tox config formats**: tox.ini, pyproject.toml, setup.cfg


## Troubleshooting

### Import errors from stubbed packages

If you see errors like `AttributeError: module 'virtualenv' has no attribute 'foo'`:

1. Check which stubbed package is missing the attribute
2. Add the attribute to the corresponding stub module file (e.g., `_vendored/virtualenv/__init__.py`)
3. Run tests to verify the fix

### Patch application failures

If `vendor.py` reports patch failures:

1. Check if tox refactored the patched files
2. Manually apply the changes as described in "If Patches Fail to Apply"
3. Regenerate `tox.patch`
4. Consider if the patch is still needed

### Config extraction errors

If `read_tox_config()` fails on a previously working package:

1. Test with upstream tox to see if it's a tox regression
2. Check if new tox version uses features we stub
3. Update stubs as needed

### Import isolation issues

If user code is getting stubs instead of real packages:

1. Verify the MetaPathFinder is installed: Check `sys.meta_path[0].__class__.__name__ == "_VendoredImportFinder"`
2. Check finder behavior: `sys.meta_path[0].find_spec('your_module', None)` should return `None` for non-tox modules
3. Verify stub modules have correct `__path__`: Package stubs need `__path__ = [str(Path(__file__).parent)]`

## License Compliance

Vendored tox is distributed under its original MIT license. The license file is copied to `src/toxology/_vendored/tox/LICENSE` during vendoring.
