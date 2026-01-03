"""Tests for Django template tags."""

import pytest
from django.template import Context, Template


@pytest.fixture
def registry_with_icons(sample_svg):
    """Set up global registry with test icons."""
    from djicons.registry import IconRegistry

    # Reset singleton to ensure clean state
    IconRegistry._instance = None
    registry = IconRegistry()

    registry.register("home", sample_svg, namespace="ion")
    registry.register("cart", sample_svg, namespace="ion")
    registry.register("pencil", sample_svg, namespace="hero")

    yield registry

    # Clean up singleton after test
    IconRegistry._instance = None


@pytest.mark.django_db
class TestIconTemplateTag:
    """Test {% icon %} template tag."""

    def test_basic_usage(self, registry_with_icons):
        """Should render icon."""
        template = Template('{% load djicons %}{% icon "ion:home" %}')
        html = template.render(Context({}))

        assert "<svg" in html

    def test_with_size(self, registry_with_icons):
        """Should render with size."""
        template = Template('{% load djicons %}{% icon "ion:home" size=32 %}')
        html = template.render(Context({}))

        assert 'width="32"' in html
        assert 'height="32"' in html

    def test_with_css_class(self, registry_with_icons):
        """Should render with CSS class."""
        template = Template('{% load djicons %}{% icon "ion:home" css_class="text-primary" %}')
        html = template.render(Context({}))

        assert "text-primary" in html

    def test_with_color(self, registry_with_icons):
        """Should render with color."""
        template = Template('{% load djicons %}{% icon "ion:home" color="#ff0000" %}')
        html = template.render(Context({}))

        assert "#ff0000" in html

    def test_with_aria_label(self, registry_with_icons):
        """Should render with aria-label."""
        template = Template('{% load djicons %}{% icon "ion:home" aria_label="Home" %}')
        html = template.render(Context({}))

        assert 'aria-label="Home"' in html
        assert 'role="img"' in html

    def test_with_data_attributes(self, registry_with_icons):
        """Should render with data attributes."""
        template = Template('{% load djicons %}{% icon "ion:home" data_action="click" %}')
        html = template.render(Context({}))

        assert 'data-action="click"' in html

    def test_missing_icon_silent(self, fresh_registry):
        """Should return empty for missing icon."""
        template = Template('{% load djicons %}{% icon "nonexistent" %}')
        html = template.render(Context({}))

        assert html.strip() == ""

    def test_icon_as_variable(self, registry_with_icons):
        """Should store icon in variable."""
        template = Template('{% load djicons %}{% icon "ion:home" as home_icon %}{{ home_icon }}')
        html = template.render(Context({}))

        assert "<svg" in html


@pytest.mark.django_db
class TestIconExistsTag:
    """Test {% icon_exists %} template tag."""

    def test_exists(self, registry_with_icons):
        """Should return True for existing icon."""
        template = Template("""
            {% load djicons %}
            {% icon_exists "ion:home" as exists %}
            {% if exists %}found{% endif %}
        """)
        html = template.render(Context({}))

        assert "found" in html

    def test_not_exists(self, fresh_registry):
        """Should return False for missing icon."""
        template = Template("""
            {% load djicons %}
            {% icon_exists "nonexistent" as exists %}
            {% if not exists %}not found{% endif %}
        """)
        html = template.render(Context({}))

        assert "not found" in html


@pytest.mark.django_db
class TestIconListTag:
    """Test {% icon_list %} template tag."""

    def test_list_namespace(self, registry_with_icons):
        """Should list icons in namespace."""
        template = Template("""
            {% load djicons %}
            {% icon_list "ion" as icons %}
            {% for name in icons %}{{ name }},{% endfor %}
        """)
        html = template.render(Context({}))

        assert "home" in html
        assert "cart" in html
