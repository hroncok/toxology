#!/usr/bin/env python3
"""Run read_tox_config(py314) on .fedpkg/*/*-build/*/ dirs (excluding SPECPARTS) and print results."""
from pathlib import Path

from toxology import read_tox_config

ROOT = Path(__file__).resolve().parent
FEDPKG = ROOT / ".fedpkg"
ENV = "py314"


def find_project_dirs():
    """Yield path for each .fedpkg/*/*-build/<name>/ where name not in (SPECPARTS, .tox)."""
    for build_dir in FEDPKG.glob("*/*-build"):
        for sub in build_dir.iterdir():
            if not sub.is_dir() or sub.name in ("SPECPARTS", ".tox"):
                continue
            yield sub


def main():
    dirs = sorted(find_project_dirs())
    print(f"Found {len(dirs)} project dirs. Running read_tox_config({ENV!r}) on each.\n")
    results = []
    for path in dirs:
        rel = path.relative_to(ROOT)
        try:
            config = read_tox_config(ENV, path=path)
            results.append((rel, None, config))
        except Exception as e:
            results.append((rel, e, None))
    # Output for inspection
    for rel, err, config in results:
        print("=" * 60)
        print("PATH:", rel)
        if err:
            print("ERROR:", type(err).__name__, err)
        else:
            print("name:", config.name)
            print("deps:", config.deps)
            print("extras:", config.extras)
            print("dependency_groups:", config.dependency_groups)
            print("commands:", [tuple(c.args) for c in config.commands])
        print()
    # Summary
    ok = sum(1 for _, e, _ in results if e is None)
    print("=" * 60)
    print(f"Summary: {ok}/{len(results)} succeeded, {len(results) - ok} failed.")


if __name__ == "__main__":
    main()
