"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_svg() -> str:
    """Sample SVG content for testing."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
</svg>'''


@pytest.fixture
def sample_svg_with_class() -> str:
    """Sample SVG with existing class."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" class="existing-class" viewBox="0 0 24 24">
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
</svg>'''


@pytest.fixture
def icons_dir(sample_svg):
    """Create a temporary directory with sample icons."""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_path = Path(tmpdir)

        # Create sample icons
        (icons_path / "home.svg").write_text(sample_svg)
        (icons_path / "cart.svg").write_text(sample_svg.replace("M10", "M15"))
        (icons_path / "settings.svg").write_text(sample_svg.replace("M10", "M20"))

        yield icons_path


@pytest.fixture
def fresh_registry():
    """Get a fresh registry instance for testing."""
    from djicons.registry import IconRegistry

    # Reset singleton for testing
    IconRegistry._instance = None
    registry = IconRegistry()

    yield registry

    # Clean up
    IconRegistry._instance = None


@pytest.fixture
def module_dir(sample_svg):
    """Create a mock ERPlora module directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        module_path = Path(tmpdir) / "inventory"
        icons_path = module_path / "static" / "icons"
        icons_path.mkdir(parents=True)

        # Create module icon
        (icons_path / "icon.svg").write_text(sample_svg)
        (icons_path / "box.svg").write_text(sample_svg.replace("M10", "M5"))

        yield module_path
