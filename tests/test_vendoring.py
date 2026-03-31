"""Tests for vendoring verification."""

import json
from importlib.metadata import distribution
from pathlib import Path

import pytest

# SBOM file paths
SBOM_SOURCE_TREE = Path(__file__).parent.parent / "src/toxology/_vendored/sbom.json"


def get_sbom_installed_path() -> Path:
    """Get path to installed SBOM in .dist-info/sboms/ directory."""
    try:
        dist = distribution("toxology")
    except ModuleNotFoundError:
        raise pytest.skip("toxology not installed, cannot check installed SBOM")

    assert dist.files is not None

    for file in dist.files:
        # Look for sbom.json in the dist-info sboms directory
        # The file path will be something like "toxology-0.1.0.dist-info/sboms/sbom.json"
        if file.match("*.dist-info/sboms/sbom.json"):
            located = Path(file.locate())
            assert located.exists()
            return located

    raise FileNotFoundError("sbom.json not found in installed distribution files")


class TestVendoringVerification:
    """Verify vendoring works correctly."""

    def test_vendor_py_script_exists(self) -> None:
        """Vendor script should exist and be executable."""
        vendor_script = Path(__file__).parent.parent / "vendor.py"
        assert vendor_script.exists(), "vendor.py script not found"
        assert vendor_script.is_file(), "vendor.py is not a file"

    def test_vendor_txt_exists(self) -> None:
        """vendor.txt should document what's vendored."""
        vendor_txt = Path(__file__).parent.parent / "src/toxology/_vendored/vendor.txt"
        assert vendor_txt.exists(), "vendor.txt not found"
        content = vendor_txt.read_text()
        assert "tox==" in content, "vendor.txt doesn't document tox version"
        assert "Vendored at:" in content, "vendor.txt doesn't document vendoring date"

    def test_vendored_tox_exists(self) -> None:
        """Vendored tox package should exist."""
        tox_dir = Path(__file__).parent.parent / "src/toxology/_vendored/tox"
        assert tox_dir.exists(), "Vendored tox directory not found"
        assert tox_dir.is_dir(), "Vendored tox is not a directory"
        # Check for key files
        assert (tox_dir / "__init__.py").exists(), "tox/__init__.py not found"
        assert (tox_dir / "plugin" / "manager.py").exists(), "tox/plugin/manager.py not found"

    def test_patches_applied(self) -> None:
        """Verify patches are applied to vendored tox."""
        manager_py = Path(__file__).parent.parent / "src/toxology/_vendored/tox/plugin/manager.py"
        content = manager_py.read_text()
        assert "# TOXOLOGY:" in content, "TOXOLOGY comment marker not found in manager.py"
        assert "Skip external plugins" in content, "External plugin patch not applied"

    def test_sbom_exists_in_source_tree(self) -> None:
        """SBOM file should exist in source tree."""
        assert SBOM_SOURCE_TREE.exists(), f"sbom.json not found in source tree: {SBOM_SOURCE_TREE}"
        assert SBOM_SOURCE_TREE.is_file(), f"sbom.json is not a file: {SBOM_SOURCE_TREE}"

    def test_sbom_exists_in_installed_package(self) -> None:
        """SBOM should be present in installed package .dist-info/sboms/ directory."""
        sbom_path = get_sbom_installed_path()
        assert sbom_path.exists(), f"sbom.json not found in installed package: {sbom_path}"
        assert sbom_path.is_file(), f"sbom.json is not a file: {sbom_path}"

    @pytest.mark.parametrize("sbom_location", ["source_tree", "installed"])
    def test_sbom_is_valid_json(self, sbom_location: str) -> None:
        """SBOM should be valid JSON."""
        sbom_file = SBOM_SOURCE_TREE if sbom_location == "source_tree" else get_sbom_installed_path()

        try:
            with open(sbom_file) as f:
                sbom = json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"SBOM at {sbom_file} is not valid JSON: {e}") from e

        assert isinstance(sbom, dict), f"SBOM at {sbom_file} root should be a dictionary"

    @pytest.mark.parametrize("sbom_location", ["source_tree", "installed"])
    def test_sbom_has_cyclonedx_structure(self, sbom_location: str) -> None:
        """SBOM should have CycloneDX 1.6 structure."""
        sbom_file = SBOM_SOURCE_TREE if sbom_location == "source_tree" else get_sbom_installed_path()

        with open(sbom_file) as f:
            sbom = json.load(f)

        # Check required top-level fields
        assert sbom.get("bomFormat") == "CycloneDX", f"bomFormat should be 'CycloneDX' in {sbom_file}"
        assert sbom.get("specVersion") == "1.6", f"specVersion should be '1.6' in {sbom_file}"
        assert "serialNumber" in sbom, f"serialNumber is required in {sbom_file}"
        assert sbom["serialNumber"].startswith("urn:uuid:"), f"serialNumber should be a UUID URN in {sbom_file}"
        assert sbom.get("version") == 1, f"version should be 1 in {sbom_file}"

        # Check metadata
        assert "metadata" in sbom, f"metadata is required in {sbom_file}"
        assert "timestamp" in sbom["metadata"], f"metadata.timestamp is required in {sbom_file}"
        assert "component" in sbom["metadata"], f"metadata.component is required in {sbom_file}"

        # Check components array
        assert "components" in sbom, f"components array is required in {sbom_file}"
        assert isinstance(sbom["components"], list), f"components should be a list in {sbom_file}"

    @pytest.mark.parametrize("sbom_location", ["source_tree", "installed"])
    def test_sbom_documents_toxology(self, sbom_location: str) -> None:
        """SBOM should document toxology as primary component."""
        sbom_file = SBOM_SOURCE_TREE if sbom_location == "source_tree" else get_sbom_installed_path()

        with open(sbom_file) as f:
            sbom = json.load(f)

        primary = sbom["metadata"]["component"]
        assert primary.get("name") == "toxology", f"Primary component should be 'toxology' in {sbom_file}"
        assert primary.get("type") == "library", f"Primary component type should be 'library' in {sbom_file}"
        assert "version" in primary, f"Primary component should have version in {sbom_file}"
        assert "purl" in primary, f"Primary component should have PURL in {sbom_file}"
        assert primary["purl"].startswith("pkg:pypi/toxology@"), f"PURL should be for toxology in {sbom_file}"

    @pytest.mark.parametrize("sbom_location", ["source_tree", "installed"])
    def test_sbom_documents_vendored_tox(self, sbom_location: str) -> None:
        """SBOM should document vendored tox with version and license."""
        sbom_file = SBOM_SOURCE_TREE if sbom_location == "source_tree" else get_sbom_installed_path()

        with open(sbom_file) as f:
            sbom = json.load(f)

        # Find tox component
        tox_components = [c for c in sbom["components"] if c.get("name") == "tox"]
        assert len(tox_components) == 1, f"Should have exactly one tox component in {sbom_file}"

        tox = tox_components[0]
        assert tox.get("type") == "library", f"tox type should be 'library' in {sbom_file}"
        assert "version" in tox, f"tox should have version in {sbom_file}"
        assert tox["version"].startswith("4."), f"tox version should start with 4. in {sbom_file}"
        assert tox.get("scope") == "required", f"tox scope should be 'required' (bundled) in {sbom_file}"

        # Check license
        assert "licenses" in tox, f"tox should have licenses in {sbom_file}"
        assert isinstance(tox["licenses"], list), f"licenses should be a list in {sbom_file}"
        assert len(tox["licenses"]) > 0, f"tox should have at least one license in {sbom_file}"
        # Check first license has MIT
        first_license = tox["licenses"][0]
        assert "license" in first_license, f"license entry should have 'license' field in {sbom_file}"
        assert first_license["license"].get("id") == "MIT", f"tox license should be MIT in {sbom_file}"

        # Check PURL
        assert "purl" in tox, f"tox should have PURL in {sbom_file}"
        assert tox["purl"].startswith("pkg:pypi/tox@"), f"PURL should be for tox in {sbom_file}"

    @pytest.mark.parametrize("sbom_location", ["source_tree", "installed"])
    def test_sbom_documents_dependency_relationship(self, sbom_location: str) -> None:
        """SBOM should document that toxology depends on tox."""
        sbom_file = SBOM_SOURCE_TREE if sbom_location == "source_tree" else get_sbom_installed_path()

        with open(sbom_file) as f:
            sbom = json.load(f)

        assert "dependencies" in sbom, f"SBOM should have dependencies array in {sbom_file}"
        assert isinstance(sbom["dependencies"], list), f"dependencies should be a list in {sbom_file}"

        # Find toxology dependency entry
        toxology_deps = [d for d in sbom["dependencies"] if "toxology" in d.get("ref", "")]
        assert len(toxology_deps) > 0, f"Should have dependency entry for toxology in {sbom_file}"

        toxology_dep = toxology_deps[0]
        assert "dependsOn" in toxology_dep, f"toxology dependency should have dependsOn in {sbom_file}"
        assert isinstance(toxology_dep["dependsOn"], list), f"dependsOn should be a list in {sbom_file}"

        # Check that tox is listed as a dependency
        tox_purls = [dep for dep in toxology_dep["dependsOn"] if "tox@" in dep]
        assert len(tox_purls) > 0, f"toxology should depend on tox in {sbom_file}"
