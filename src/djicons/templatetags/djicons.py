"""
Django template tags for djicons.

Usage:
    {% load djicons %}

    {# Basic usage #}
    {% icon "home" %}

    {# With namespace #}
    {% icon "ion:cart-outline" %}
    {% icon "hero:pencil" size=20 %}

    {# With styling #}
    {% icon "settings" size=24 css_class="text-primary" %}
    {% icon "close" color="#ff0000" %}

    {# With ARIA #}
    {% icon "menu" aria_label="Open menu" %}

    {# With data attributes #}
    {% icon "close" data_action="dismiss" data_target="#modal" %}

    {# Store in variable #}
    {% icon "home" as home_icon %}
    {{ home_icon }}
"""

from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


def _get_registry():
    """Get the current icon registry instance."""
    from ..registry import IconRegistry

    return IconRegistry()


@register.simple_tag
def icon(
    name: str,
    size: int | None = None,
    width: int | None = None,
    height: int | None = None,
    css_class: str = "",
    color: str = "",
    fill: str = "",
    stroke: str = "",
    aria_label: str = "",
    aria_hidden: bool | None = None,
    **attrs: str,
) -> SafeString:
    """
    Render an SVG icon inline.

    Args:
        name: Icon name, optionally prefixed with namespace (e.g., "ion:home")
        size: Icon size in pixels (sets both width and height)
        width: Width in pixels (overrides size)
        height: Height in pixels (overrides size)
        css_class: CSS class(es) to add
        color: CSS color value
        fill: SVG fill color
        stroke: SVG stroke color
        aria_label: Accessibility label (removes aria-hidden if set)
        aria_hidden: Hide from screen readers
        **attrs: Additional HTML attributes (underscores become dashes)

    Returns:
        Inline SVG HTML

    Examples:
        {% icon "home" %}
        {% icon "ion:cart-outline" size=24 %}
        {% icon "hero:pencil-square" css_class="w-5 h-5 text-blue-500" %}
        {% icon "settings" aria_label="Settings menu" %}
        {% icon "close" data_action="dismiss" %}
    """
    icons = _get_registry()
    icon_obj = icons.get(name)

    if icon_obj is None:
        from ..conf import get_setting

        if get_setting("MISSING_ICON_SILENT"):
            return mark_safe("")
        return mark_safe(f"<!-- Icon not found: {name} -->")

    return icon_obj.render(
        size=size,
        width=width,
        height=height,
        css_class=css_class,
        color=color,
        fill=fill,
        stroke=stroke,
        aria_label=aria_label,
        aria_hidden=aria_hidden,
        **attrs,
    )


@register.simple_tag
def icon_exists(name: str) -> bool:
    """
    Check if an icon exists.

    Usage:
        {% icon_exists "ion:home" as has_home %}
        {% if has_home %}...{% endif %}

    Args:
        name: Icon name with optional namespace

    Returns:
        True if icon exists
    """
    return _get_registry().has(name)


@register.simple_tag
def icon_list(namespace: str = "") -> list[str]:
    """
    List available icons in a namespace.

    Usage:
        {% icon_list "ion" as ionicons %}
        {% for name in ionicons %}
            {% icon name size=24 %}
        {% endfor %}

    Args:
        namespace: Namespace to list (empty for all)

    Returns:
        List of icon names
    """
    return _get_registry().list_icons(namespace if namespace else None)


@register.inclusion_tag("djicons/sprite.html")
def icon_sprite(namespace: str = "") -> dict[str, list[dict[str, str]]]:
    """
    Render an SVG sprite sheet for use with <use xlink:href="...">.

    This is useful for pages with many icons to reduce DOM size.

    Usage:
        {% icon_sprite "ion" %}

        {# Then reference icons with: #}
        <svg><use xlink:href="#icon-ion-home"></use></svg>

    Args:
        namespace: Namespace to include (empty for default)

    Returns:
        Context with list of icons for the sprite template
    """
    icons = _get_registry()
    icon_list = []
    for icon_name in icons.list_icons(namespace if namespace else None):
        icon_obj = icons.get(icon_name)
        if icon_obj:
            icon_id = f"icon-{icon_obj.qualified_name.replace(':', '-')}"
            icon_list.append(
                {
                    "id": icon_id,
                    "svg": icon_obj.svg_content,
                }
            )

    return {"icons": icon_list}
