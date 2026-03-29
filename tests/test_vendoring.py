"""Tests for vendoring verification."""

import json
from importlib.metadata import distribution
from pathlib import Path


class TestVendoringVerification:
    """Verify vendoring works correctly."""

    def test_vendor_py_script_exists(self) -> None:
        """Vendor script should exist and be executable."""
        vendor_script = Path(__file__).parent.parent / "vendor.py"
        assert vendor_script.exists(), "vendor.py script not found"
        assert vendor_script.is_file(), "vendor.py is not a file"

    def test_vendor_txt_exists(self) -> None:
        """vendor.txt should document what's vendored."""
        vendor_txt = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "vendor.txt"
        assert vendor_txt.exists(), "vendor.txt not found"
        content = vendor_txt.read_text()
        assert "tox==" in content, "vendor.txt doesn't document tox version"
        assert "Vendored at:" in content, "vendor.txt doesn't document vendoring date"

    def test_vendored_tox_exists(self) -> None:
        """Vendored tox package should exist."""
        tox_dir = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox"
        assert tox_dir.exists(), "Vendored tox directory not found"
        assert tox_dir.is_dir(), "Vendored tox is not a directory"
        # Check for key files
        assert (tox_dir / "__init__.py").exists(), "tox/__init__.py not found"
        assert (tox_dir / "plugin" / "manager.py").exists(), "tox/plugin/manager.py not found"

    def test_patches_applied(self) -> None:
        """Verify patches are applied to vendored tox."""
        manager_py = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox" / "plugin" / "manager.py"
        content = manager_py.read_text()
        assert "# TOXOLOGY:" in content, "TOXOLOGY comment marker not found in manager.py"
        assert "Skip external plugins" in content, "External plugin patch not applied"

        sets_py = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "tox" / "config" / "sets.py"
        content = sets_py.read_text()
        assert "# TOXOLOGY:" in content, "TOXOLOGY comment marker not found in sets.py"

    def test_sbom_exists_in_source_tree(self) -> None:
        """SBOM file should exist in source tree."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        assert sbom_file.exists(), "sbom.json not found in source tree"
        assert sbom_file.is_file(), "sbom.json is not a file"

    def test_sbom_is_valid_json(self) -> None:
        """SBOM should be valid JSON."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        try:
            with open(sbom_file) as f:
                sbom = json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"SBOM is not valid JSON: {e}") from e

        assert isinstance(sbom, dict), "SBOM root should be a dictionary"

    def test_sbom_has_cyclonedx_structure(self) -> None:
        """SBOM should have CycloneDX 1.6 structure."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        with open(sbom_file) as f:
            sbom = json.load(f)

        # Check required top-level fields
        assert sbom.get("bomFormat") == "CycloneDX", "bomFormat should be 'CycloneDX'"
        assert sbom.get("specVersion") == "1.6", "specVersion should be '1.6'"
        assert "serialNumber" in sbom, "serialNumber is required"
        assert sbom["serialNumber"].startswith("urn:uuid:"), "serialNumber should be a UUID URN"
        assert sbom.get("version") == 1, "version should be 1"

        # Check metadata
        assert "metadata" in sbom, "metadata is required"
        assert "timestamp" in sbom["metadata"], "metadata.timestamp is required"
        assert "component" in sbom["metadata"], "metadata.component is required"

        # Check components array
        assert "components" in sbom, "components array is required"
        assert isinstance(sbom["components"], list), "components should be a list"

    def test_sbom_documents_toxology(self) -> None:
        """SBOM should document toxology as primary component."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        with open(sbom_file) as f:
            sbom = json.load(f)

        primary = sbom["metadata"]["component"]
        assert primary.get("name") == "toxology", "Primary component should be 'toxology'"
        assert primary.get("type") == "library", "Primary component type should be 'library'"
        assert "version" in primary, "Primary component should have version"
        assert "purl" in primary, "Primary component should have PURL"
        assert primary["purl"].startswith("pkg:pypi/toxology@"), "PURL should be for toxology"

    def test_sbom_documents_vendored_tox(self) -> None:
        """SBOM should document vendored tox with version and license."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        with open(sbom_file) as f:
            sbom = json.load(f)

        # Find tox component
        tox_components = [c for c in sbom["components"] if c.get("name") == "tox"]
        assert len(tox_components) == 1, "Should have exactly one tox component"

        tox = tox_components[0]
        assert tox.get("type") == "library", "tox type should be 'library'"
        assert "version" in tox, "tox should have version"
        assert tox["version"].startswith("4."), "tox version should start with 4."
        assert tox.get("scope") == "required", "tox scope should be 'required' (bundled)"

        # Check license
        assert "licenses" in tox, "tox should have licenses"
        assert isinstance(tox["licenses"], list), "licenses should be a list"
        assert len(tox["licenses"]) > 0, "tox should have at least one license"
        # Check first license has MIT
        first_license = tox["licenses"][0]
        assert "license" in first_license, "license entry should have 'license' field"
        assert first_license["license"].get("id") == "MIT", "tox license should be MIT"

        # Check PURL
        assert "purl" in tox, "tox should have PURL"
        assert tox["purl"].startswith("pkg:pypi/tox@"), "PURL should be for tox"

    def test_sbom_documents_dependency_relationship(self) -> None:
        """SBOM should document that toxology depends on tox."""
        sbom_file = Path(__file__).parent.parent / "src" / "toxology" / "_vendored" / "sbom.json"
        with open(sbom_file) as f:
            sbom = json.load(f)

        assert "dependencies" in sbom, "SBOM should have dependencies array"
        assert isinstance(sbom["dependencies"], list), "dependencies should be a list"

        # Find toxology dependency entry
        toxology_deps = [d for d in sbom["dependencies"] if "toxology" in d.get("ref", "")]
        assert len(toxology_deps) > 0, "Should have dependency entry for toxology"

        toxology_dep = toxology_deps[0]
        assert "dependsOn" in toxology_dep, "toxology dependency should have dependsOn"
        assert isinstance(toxology_dep["dependsOn"], list), "dependsOn should be a list"

        # Check that tox is listed as a dependency
        tox_purls = [dep for dep in toxology_dep["dependsOn"] if "tox@" in dep]
        assert len(tox_purls) > 0, "toxology should depend on tox"

    def test_sbom_exists_in_installed_package(self) -> None:
        """SBOM should be present in installed package .dist-info/sboms/ directory."""
        # Get the distribution object for toxology
        dist = distribution("toxology")

        # Find the .dist-info directory location
        # The dist._path attribute points to the .dist-info directory
        dist_info_path = Path(str(dist._path))
        assert dist_info_path.exists(), f"dist-info directory not found: {dist_info_path}"

        # Check for sboms subdirectory
        sboms_dir = dist_info_path / "sboms"
        assert sboms_dir.exists(), f"sboms directory not found in {dist_info_path}"
        assert sboms_dir.is_dir(), f"sboms is not a directory: {sboms_dir}"

        # Check for sbom.json in sboms directory
        installed_sbom = sboms_dir / "sbom.json"
        assert installed_sbom.exists(), f"sbom.json not found in {sboms_dir}"
        assert installed_sbom.is_file(), f"sbom.json is not a file: {installed_sbom}"

        # Verify it's valid JSON with correct structure
        with open(installed_sbom) as f:
            sbom = json.load(f)

        assert sbom.get("bomFormat") == "CycloneDX", "Installed SBOM should be CycloneDX format"
        assert sbom.get("specVersion") == "1.6", "Installed SBOM should be version 1.6"

        # Verify it documents tox
        tox_components = [c for c in sbom.get("components", []) if c.get("name") == "tox"]
        assert len(tox_components) == 1, "Installed SBOM should document tox"
