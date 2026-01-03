"""Tests for IconRegistry."""

import pytest
from djicons.registry import IconRegistry, icons
from djicons.icon import Icon


class TestIconRegistry:
    """Test IconRegistry functionality."""

    def test_singleton_pattern(self, fresh_registry):
        """Registry should be a singleton."""
        registry1 = IconRegistry()
        registry2 = IconRegistry()
        assert registry1 is registry2

    def test_register_icon(self, fresh_registry, sample_svg):
        """Should register an icon."""
        icon = fresh_registry.register("home", sample_svg, namespace="test")

        assert isinstance(icon, Icon)
        assert icon.name == "home"
        assert icon.namespace == "test"
        assert icon.qualified_name == "test:home"

    def test_get_icon_with_namespace(self, fresh_registry, sample_svg):
        """Should get icon with explicit namespace."""
        fresh_registry.register("home", sample_svg, namespace="ion")

        icon = fresh_registry.get("ion:home")
        assert icon is not None
        assert icon.name == "home"
        assert icon.namespace == "ion"

    def test_get_icon_without_namespace(self, fresh_registry, sample_svg):
        """Should get icon from default namespace."""
        fresh_registry.register("home", sample_svg, namespace="ion")

        # With default namespace set
        icon = fresh_registry.get("home", namespace="ion")
        assert icon is not None
        assert icon.name == "home"

    def test_get_nonexistent_icon(self, fresh_registry):
        """Should return None for nonexistent icon."""
        icon = fresh_registry.get("nonexistent")
        assert icon is None

    def test_has_icon(self, fresh_registry, sample_svg):
        """Should check icon existence."""
        fresh_registry.register("home", sample_svg, namespace="test")

        assert fresh_registry.has("test:home")
        assert not fresh_registry.has("test:nonexistent")

    def test_contains_operator(self, fresh_registry, sample_svg):
        """Should support 'in' operator."""
        fresh_registry.register("home", sample_svg, namespace="test")

        assert "test:home" in fresh_registry
        assert "test:nonexistent" not in fresh_registry

    def test_list_icons(self, fresh_registry, sample_svg):
        """Should list registered icons."""
        fresh_registry.register("home", sample_svg, namespace="ion")
        fresh_registry.register("cart", sample_svg, namespace="ion")
        fresh_registry.register("star", sample_svg, namespace="hero")

        all_icons = fresh_registry.list_icons()
        assert "ion:home" in all_icons
        assert "ion:cart" in all_icons
        assert "hero:star" in all_icons

        ion_icons = fresh_registry.list_icons("ion")
        assert "home" in ion_icons
        assert "cart" in ion_icons
        assert "star" not in ion_icons

    def test_list_namespaces(self, fresh_registry, sample_svg):
        """Should list all namespaces."""
        fresh_registry.register("home", sample_svg, namespace="ion")
        fresh_registry.register("star", sample_svg, namespace="hero")

        namespaces = fresh_registry.list_namespaces()
        assert "ion" in namespaces
        assert "hero" in namespaces

    def test_alias(self, fresh_registry, sample_svg):
        """Should resolve aliases."""
        fresh_registry.register("pencil", sample_svg, namespace="hero")
        fresh_registry.register_alias("edit", "hero:pencil")

        icon = fresh_registry.get("edit")
        assert icon is not None
        assert icon.name == "pencil"
        assert icon.namespace == "hero"

    def test_clear_namespace(self, fresh_registry, sample_svg):
        """Should clear specific namespace."""
        fresh_registry.register("home", sample_svg, namespace="ion")
        fresh_registry.register("star", sample_svg, namespace="hero")

        fresh_registry.clear("ion")

        assert fresh_registry.get("ion:home") is None
        assert fresh_registry.get("hero:star") is not None

    def test_clear_all(self, fresh_registry, sample_svg):
        """Should clear all icons."""
        fresh_registry.register("home", sample_svg, namespace="ion")
        fresh_registry.register("star", sample_svg, namespace="hero")

        fresh_registry.clear()

        assert len(fresh_registry) == 0

    def test_len(self, fresh_registry, sample_svg):
        """Should return total icon count."""
        fresh_registry.register("home", sample_svg, namespace="ion")
        fresh_registry.register("cart", sample_svg, namespace="ion")
        fresh_registry.register("star", sample_svg, namespace="hero")

        assert len(fresh_registry) == 3
