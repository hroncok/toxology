"""Tests for vendoring verification."""

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
