#!/usr/bin/env python3
"""Semi-automated vendoring script for toxology.

Vendors tox and applies patches from tox.patch.
All other dependencies are stubbed.

Usage:
    python vendor.py              # Vendor latest tox from PyPI
    python vendor.py --version 4.23.2  # Vendor specific version
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ImportError:
    # Python < 3.11 fallback
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

REPO_ROOT = Path(__file__).parent
VENDOR_DIR = REPO_ROOT / "src/toxology/_vendored"
VENDOR_TXT = VENDOR_DIR / "vendor.txt"
PATCH_FILE = REPO_ROOT / "tox.patch"


def get_latest_tox_version() -> str:
    """Query PyPI for latest tox version."""
    url = "https://pypi.org/pypi/tox/json"
    print("Querying PyPI for latest tox version...")
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        version = data["info"]["version"]
        print(f"Latest tox version: {version}")
        return version


def download_and_extract_tox(version: str, temp_dir: Path) -> Path:
    """Download tox to temp directory using pip download."""
    print(f"\nDownloading tox {version}...")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Download tox wheel/sdist
    download_dir = temp_dir / "downloads"
    download_dir.mkdir(exist_ok=True)

    # Override pip config to avoid require-virtualenv
    env = os.environ.copy()
    env["PIP_CONFIG_FILE"] = "/dev/null"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--dest",
            str(download_dir),
            f"tox=={version}",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print("✗ pip download failed:")
        print(result.stderr)
        raise RuntimeError(f"Failed to download tox {version}")

    # Find downloaded file (wheel or sdist)
    downloaded_files = list(download_dir.glob("tox-*"))
    if not downloaded_files:
        raise RuntimeError(f"No tox files found in {download_dir}")

    downloaded = downloaded_files[0]
    print(f"✓ Downloaded {downloaded.name}")

    # Extract it
    extract_dir = temp_dir / "extracted"
    if downloaded.suffix == ".whl":
        # Unzip wheel
        import zipfile

        with zipfile.ZipFile(downloaded, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    else:
        # Extract tar.gz
        import tarfile

        with tarfile.open(downloaded, "r:gz") as tar_ref:
            tar_ref.extractall(extract_dir)

    # Find tox directory in extracted content
    tox_src = extract_dir / "tox"
    if not tox_src.exists():
        # Might be in a subdirectory for sdist
        subdirs = list(extract_dir.glob("tox-*/tox"))
        if subdirs:
            tox_src = subdirs[0]
        else:
            raise RuntimeError(f"tox package not found in {extract_dir}")

    print(f"✓ Extracted tox to {tox_src}")
    return tox_src


def copy_tox_package(tox_src: Path) -> None:
    """Copy tox package to vendored directory."""
    tox_dest = VENDOR_DIR / "tox"

    # Remove old tox if exists
    if tox_dest.exists():
        print("\nRemoving old vendored tox...")
        shutil.rmtree(tox_dest)

    # Copy new tox
    print(f"Copying tox to {tox_dest}...")
    shutil.copytree(tox_src, tox_dest)
    print("✓ Copied tox package")


def copy_license(temp_dir: Path) -> None:
    """Copy LICENSE file from dist-info or extracted content."""
    # First try dist-info in extracted directory
    extract_dir = temp_dir / "extracted"
    dist_info_dirs = list(extract_dir.glob("tox-*.dist-info"))

    license_src = None

    if dist_info_dirs:
        license_src = dist_info_dirs[0] / "LICENSE"
        if not license_src.exists():
            # Try licenses directory
            licenses_dir = dist_info_dirs[0] / "licenses"
            if licenses_dir.exists():
                license_files = list(licenses_dir.glob("LICENSE*"))
                if license_files:
                    license_src = license_files[0]
                else:
                    license_src = None
            else:
                license_src = None

    # If not found in dist-info, try root of extracted sdist
    if not license_src or not license_src.exists():
        sdist_dirs = list(extract_dir.glob("tox-*/"))
        if sdist_dirs:
            license_candidates = list(sdist_dirs[0].glob("LICENSE*"))
            if license_candidates:
                license_src = license_candidates[0]

    if license_src and license_src.exists():
        license_dest = VENDOR_DIR / "tox" / "LICENSE"
        shutil.copy2(license_src, license_dest)
        print(f"✓ Copied LICENSE from {license_src.name}")
    else:
        print("⚠ Warning: LICENSE file not found")


def apply_patches() -> None:
    """Apply patches from tox.patch."""
    print("\nApplying patches...")

    if not PATCH_FILE.exists():
        raise RuntimeError(f"Patch file not found: {PATCH_FILE}")

    tox_dir = VENDOR_DIR / "tox"
    if not tox_dir.exists():
        raise RuntimeError(f"Vendored tox directory not found: {tox_dir}")

    # Try applying with patch command (most portable)
    result = subprocess.run(
        ["patch", "-p0", "-d", str(tox_dir), "-i", str(PATCH_FILE)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"✓ Applied patches from {PATCH_FILE.name}")
        return

    # If patch failed, try git apply
    result = subprocess.run(
        ["git", "apply", "--directory", "src/toxology/_vendored/tox", str(PATCH_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode == 0:
        print(f"✓ Applied patches from {PATCH_FILE.name}")
        return

    # Both failed - provide helpful error message
    print(f"✗ Failed to apply patches from {PATCH_FILE.name}")
    print("\nThe patch file may need to be updated for this tox version.")
    print("This usually happens when tox changes the files we patch.\n")
    print("To fix this:")
    print(f"  1. Manually edit files in {tox_dir.relative_to(REPO_ROOT)}")
    print(f"  2. Regenerate the patch: cd {REPO_ROOT} && git diff src/toxology/_vendored/tox > tox.patch")
    print("  3. Re-run: python vendor.py --version <version>")
    print("\nPatch output:")
    print(result.stderr)
    raise RuntimeError("Patch application failed")


def update_vendor_txt(version: str) -> None:
    """Update vendor.txt with vendored tox version."""
    print(f"\nUpdating {VENDOR_TXT.relative_to(REPO_ROOT)}...")

    today = datetime.now().strftime("%Y-%m-%d")
    content = f"# Vendored at: {today}\ntox=={version}\n"

    VENDOR_TXT.write_text(content)
    print(f"✓ Updated vendor.txt with tox {version}")


def get_toxology_version() -> str:
    """Get toxology version from pyproject.toml."""
    pyproject = REPO_ROOT / "pyproject.toml"
    try:
        if tomllib is None:
            # Fallback: simple regex parsing
            content = pyproject.read_text()
            import re
            match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if match:
                return match.group(1)
            raise ValueError("version not found in pyproject.toml")

        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception as e:
        print(f"⚠ Warning: Could not read version from pyproject.toml: {e}")
        return "0.0.0"


def generate_sbom(tox_version: str) -> None:
    """Generate CycloneDX SBOM documenting vendored tox."""
    print("\nGenerating SBOM...")

    toxology_version = get_toxology_version()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    serial_number = f"urn:uuid:{uuid.uuid4()}"

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": serial_number,
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "vendor.py",
                        "version": "1.0"
                    }
                ]
            },
            "component": {
                "type": "library",
                "bom-ref": f"pkg:pypi/toxology@{toxology_version}",
                "name": "toxology",
                "version": toxology_version,
                "purl": f"pkg:pypi/toxology@{toxology_version}"
            }
        },
        "components": [
            {
                "type": "library",
                "bom-ref": f"pkg:pypi/tox@{tox_version}",
                "name": "tox",
                "version": tox_version,
                "scope": "required",
                "licenses": [
                    {
                        "license": {
                            "id": "MIT"
                        }
                    }
                ],
                "purl": f"pkg:pypi/tox@{tox_version}",
                "externalReferences": [
                    {
                        "type": "website",
                        "url": "https://tox.wiki"
                    },
                    {
                        "type": "vcs",
                        "url": "https://github.com/tox-dev/tox"
                    }
                ]
            }
        ],
        "dependencies": [
            {
                "ref": f"pkg:pypi/toxology@{toxology_version}",
                "dependsOn": [
                    f"pkg:pypi/tox@{tox_version}"
                ]
            }
        ]
    }

    sbom_file = VENDOR_DIR / "sbom.json"
    with open(sbom_file, "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Trailing newline

    print(f"✓ Generated SBOM at {sbom_file.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vendor tox for toxology")
    parser.add_argument(
        "--version",
        help="Tox version to vendor (default: latest from PyPI)",
    )
    args = parser.parse_args()

    # Get version
    version = args.version or get_latest_tox_version()

    # Create temp directory
    temp_dir = Path("/tmp/toxology_vendor")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    try:
        # Download tox
        tox_src = download_and_extract_tox(version, temp_dir)

        # Ensure vendor directory exists
        VENDOR_DIR.mkdir(parents=True, exist_ok=True)

        # Copy tox package
        copy_tox_package(tox_src)

        # Copy LICENSE
        copy_license(temp_dir)

        # Apply patches
        apply_patches()

        # Generate SBOM
        generate_sbom(version)

        # Update vendor.txt
        update_vendor_txt(version)

        print(f"\n✅ Successfully vendored tox {version}")
        print("\nNext steps:")
        print(f"  1. Review changes: git diff {VENDOR_DIR.relative_to(REPO_ROOT)}")
        print("  2. Run tests: tox run -e py312")
        print(f"  3. Commit: git add {VENDOR_DIR.relative_to(REPO_ROOT)} && git commit -m 'Vendor tox {version}'")

    finally:
        # Cleanup temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
