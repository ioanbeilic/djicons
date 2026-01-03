"""Tests for Icon class."""

import pytest
from djicons.icon import Icon


class TestIcon:
    """Test Icon functionality."""

    def test_init(self, sample_svg):
        """Should initialize icon with properties."""
        icon = Icon("home", sample_svg, namespace="ion", category="navigation")

        assert icon.name == "home"
        assert icon.namespace == "ion"
        assert icon.category == "navigation"
        assert icon.qualified_name == "ion:home"

    def test_qualified_name_without_namespace(self, sample_svg):
        """Should return name only if no namespace."""
        icon = Icon("home", sample_svg)
        assert icon.qualified_name == "home"

    def test_render_basic(self, sample_svg):
        """Should render SVG."""
        icon = Icon("home", sample_svg)
        html = icon.render()

        assert "<svg" in html
        assert "</svg>" in html
        assert "aria-hidden" in html

    def test_render_with_size(self, sample_svg):
        """Should render with custom size."""
        icon = Icon("home", sample_svg)
        html = icon.render(size=32)

        assert 'width="32"' in html
        assert 'height="32"' in html

    def test_render_with_width_height(self, sample_svg):
        """Should render with separate width/height."""
        icon = Icon("home", sample_svg)
        html = icon.render(width=24, height=32)

        assert 'width="24"' in html
        assert 'height="32"' in html

    def test_render_with_css_class(self, sample_svg):
        """Should add CSS class."""
        icon = Icon("home", sample_svg)
        html = icon.render(css_class="text-primary icon-lg")

        assert 'class="text-primary icon-lg"' in html

    def test_render_with_existing_class(self, sample_svg_with_class):
        """Should append to existing class."""
        icon = Icon("home", sample_svg_with_class)
        html = icon.render(css_class="new-class")

        assert "existing-class" in html
        assert "new-class" in html

    def test_render_with_color(self, sample_svg):
        """Should add color style."""
        icon = Icon("home", sample_svg)
        html = icon.render(color="#ff0000")

        assert 'style="color: #ff0000"' in html

    def test_render_with_fill(self, sample_svg):
        """Should add fill attribute."""
        icon = Icon("home", sample_svg)
        html = icon.render(fill="currentColor")

        assert 'fill="currentColor"' in html

    def test_render_with_stroke(self, sample_svg):
        """Should add stroke attribute."""
        icon = Icon("home", sample_svg)
        html = icon.render(stroke="#000")

        assert 'stroke="#000"' in html

    def test_render_with_aria_label(self, sample_svg):
        """Should add aria-label and role."""
        icon = Icon("home", sample_svg)
        html = icon.render(aria_label="Home icon")

        assert 'aria-label="Home icon"' in html
        assert 'role="img"' in html
        assert 'aria-hidden="true"' not in html

    def test_render_with_aria_hidden(self, sample_svg):
        """Should add aria-hidden."""
        icon = Icon("home", sample_svg)
        html = icon.render(aria_hidden=True)

        assert 'aria-hidden="true"' in html

    def test_render_with_data_attributes(self, sample_svg):
        """Should add data attributes."""
        icon = Icon("home", sample_svg)
        html = icon.render(data_action="click", data_target="#modal")

        assert 'data-action="click"' in html
        assert 'data-target="#modal"' in html

    def test_render_escapes_html(self, sample_svg):
        """Should escape HTML in attributes."""
        icon = Icon("home", sample_svg)
        html = icon.render(css_class='<script>alert("xss")</script>')

        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_str(self, sample_svg):
        """Should render on str()."""
        icon = Icon("home", sample_svg)
        html = str(icon)

        assert "<svg" in html

    def test_repr(self, sample_svg):
        """Should have debug representation."""
        icon = Icon("home", sample_svg, namespace="ion")

        assert repr(icon) == "Icon('ion:home')"

    def test_equality(self, sample_svg):
        """Should compare by qualified name."""
        icon1 = Icon("home", sample_svg, namespace="ion")
        icon2 = Icon("home", sample_svg, namespace="ion")
        icon3 = Icon("cart", sample_svg, namespace="ion")

        assert icon1 == icon2
        assert icon1 != icon3

    def test_hash(self, sample_svg):
        """Should be hashable."""
        icon1 = Icon("home", sample_svg, namespace="ion")
        icon2 = Icon("home", sample_svg, namespace="ion")

        assert hash(icon1) == hash(icon2)

        # Can use in sets
        icon_set = {icon1, icon2}
        assert len(icon_set) == 1
