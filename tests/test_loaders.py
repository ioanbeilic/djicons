"""Tests for icon loaders."""

import pytest
from pathlib import Path
from djicons.loaders import DirectoryIconLoader, BaseIconLoader


class TestDirectoryIconLoader:
    """Test DirectoryIconLoader functionality."""

    def test_load_icon(self, icons_dir):
        """Should load icon from directory."""
        loader = DirectoryIconLoader(icons_dir)
        svg = loader.load("home")

        assert svg is not None
        assert "<svg" in svg

    def test_load_nonexistent(self, icons_dir):
        """Should return None for nonexistent icon."""
        loader = DirectoryIconLoader(icons_dir)
        svg = loader.load("nonexistent")

        assert svg is None

    def test_list_icons(self, icons_dir):
        """Should list available icons."""
        loader = DirectoryIconLoader(icons_dir)
        icons = loader.list()

        assert "home" in icons
        assert "cart" in icons
        assert "settings" in icons

    def test_contains(self, icons_dir):
        """Should support 'in' operator."""
        loader = DirectoryIconLoader(icons_dir)

        assert "home" in loader
        assert "nonexistent" not in loader

    def test_caching(self, icons_dir):
        """Should cache loaded icons."""
        loader = DirectoryIconLoader(icons_dir)

        svg1 = loader.load("home")
        svg2 = loader.load("home")

        assert svg1 is svg2  # Same object from cache

    def test_clear_cache(self, icons_dir):
        """Should clear cache."""
        loader = DirectoryIconLoader(icons_dir)

        loader.load("home")
        assert "home" in loader._cache

        loader.clear_cache()
        assert "home" not in loader._cache

    def test_nonexistent_directory(self, tmp_path):
        """Should handle nonexistent directory."""
        loader = DirectoryIconLoader(tmp_path / "nonexistent")

        assert loader.list() == []
        assert loader.load("anything") is None

    def test_repr(self, icons_dir):
        """Should have debug representation."""
        loader = DirectoryIconLoader(icons_dir)

        assert "DirectoryIconLoader" in repr(loader)
        assert str(icons_dir) in repr(loader)


class TestBaseIconLoader:
    """Test BaseIconLoader abstract class."""

    def test_cannot_instantiate(self):
        """Should not be instantiable."""
        with pytest.raises(TypeError):
            BaseIconLoader()

    def test_subclass_must_implement(self):
        """Subclass must implement abstract methods."""

        class IncompleteLoader(BaseIconLoader):
            pass

        with pytest.raises(TypeError):
            IncompleteLoader()

    def test_valid_subclass(self):
        """Valid subclass should work."""

        class ValidLoader(BaseIconLoader):
            def load(self, name):
                return "<svg></svg>"

            def list(self):
                return ["icon1", "icon2"]

        loader = ValidLoader()
        assert loader.load("test") == "<svg></svg>"
        assert "icon1" in loader
