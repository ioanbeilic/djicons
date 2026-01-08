"""Tests for CDN icon loader."""

from unittest.mock import MagicMock, patch

import pytest

from djicons.loaders.cdn import CDN_TEMPLATES, CDNIconLoader


class TestCDNIconLoader:
    """Tests for CDNIconLoader."""

    def test_init_with_known_namespace(self):
        """Test initialization with a known namespace."""
        loader = CDNIconLoader(namespace="ion")
        assert loader.namespace == "ion"
        assert loader.base_url == CDN_TEMPLATES["ion"]

    def test_init_with_custom_url(self):
        """Test initialization with custom URL."""
        custom_url = "https://example.com/icons/{name}.svg"
        loader = CDNIconLoader(namespace="custom", base_url=custom_url)
        assert loader.namespace == "custom"
        assert loader.base_url == custom_url

    def test_init_with_unknown_namespace_no_url(self):
        """Test initialization with unknown namespace and no URL raises error."""
        with pytest.raises(ValueError, match="No CDN URL template"):
            CDNIconLoader(namespace="unknown")

    def test_load_caches_result(self):
        """Test that loaded icons are cached."""
        loader = CDNIconLoader(namespace="ion")

        # Mock the urlopen to return SVG content
        mock_response = MagicMock()
        mock_response.read.return_value = b"<svg>test</svg>"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("djicons.loaders.cdn.urlopen", return_value=mock_response):
            # First load
            result1 = loader.load("home")
            assert result1 == "<svg>test</svg>"

            # Second load should use cache (urlopen not called again)
            result2 = loader.load("home")
            assert result2 == "<svg>test</svg>"
            assert "home" in loader._cache

    def test_load_tracks_failed_icons(self):
        """Test that failed icons are tracked to avoid retrying."""
        loader = CDNIconLoader(namespace="ion")

        from urllib.error import HTTPError

        with patch(
            "djicons.loaders.cdn.urlopen", side_effect=HTTPError(None, 404, "Not Found", {}, None)
        ):
            result = loader.load("nonexistent")
            assert result is None
            assert "nonexistent" in loader._failed

            # Second attempt should not retry
            result2 = loader.load("nonexistent")
            assert result2 is None

    def test_list_returns_cached_icons(self):
        """Test that list returns cached icon names."""
        loader = CDNIconLoader(namespace="ion")
        loader._cache = {"home": "<svg/>", "cart": "<svg/>"}

        icons = loader.list()
        assert sorted(icons) == ["cart", "home"]

    def test_clear_cache(self):
        """Test cache clearing."""
        loader = CDNIconLoader(namespace="ion")
        loader._cache = {"home": "<svg/>"}
        loader._failed = {"bad-icon"}

        loader.clear_cache()

        assert len(loader._cache) == 0
        assert len(loader._failed) == 0

    def test_repr(self):
        """Test string representation."""
        loader = CDNIconLoader(namespace="ion")
        repr_str = repr(loader)
        assert "CDNIconLoader" in repr_str
        assert "ion" in repr_str


class TestCDNTemplates:
    """Tests for CDN URL templates."""

    def test_all_namespaces_have_templates(self):
        """Test that expected namespaces have CDN templates."""
        expected = ["ion", "hero", "tabler", "lucide", "fa", "material"]
        for ns in expected:
            assert ns in CDN_TEMPLATES, f"Missing CDN template for {ns}"

    def test_templates_have_name_placeholder(self):
        """Test that all templates contain {name} placeholder."""
        for ns, url in CDN_TEMPLATES.items():
            assert "{name}" in url, f"Template for {ns} missing {{name}} placeholder"
