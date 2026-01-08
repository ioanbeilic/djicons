"""
Icon class - Represents a single SVG icon with rendering capabilities.

Usage:
    from djicons import Icon

    icon = Icon("home", "<svg>...</svg>", namespace="ion")
    html = icon.render(size=24, css_class="text-primary")
"""

from __future__ import annotations

import re
from typing import Any

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe


class Icon:
    """
    Represents a single SVG icon with rendering capabilities.

    The Icon class holds SVG content and provides methods to render it
    with custom attributes like size, CSS classes, and ARIA labels.

    Attributes:
        name: Icon identifier (e.g., "home", "cart-outline")
        namespace: Namespace (e.g., "ion", "hero", "inventory")
        svg_content: Raw SVG content as string
        category: Optional category for organization
        tags: Search tags for discoverability
    """

    # Regex patterns for SVG manipulation
    _SVG_TAG_PATTERN = re.compile(r"<svg([^>]*)>", re.IGNORECASE)
    _WIDTH_PATTERN = re.compile(r'\s*width=["\'][^"\']*["\']')
    _HEIGHT_PATTERN = re.compile(r'\s*height=["\'][^"\']*["\']')
    _CLASS_PATTERN = re.compile(r'class=["\']([^"\']*)["\']')
    _FILL_PATTERN = re.compile(r'\s*fill=["\'][^"\']*["\']')

    def __init__(
        self,
        name: str,
        svg_content: str,
        namespace: str = "",
        category: str = "",
        tags: list[str] | None = None,
        **extra: Any,
    ) -> None:
        """
        Initialize an Icon instance.

        Args:
            name: Icon identifier
            svg_content: Raw SVG content
            namespace: Namespace for the icon
            category: Category for organization
            tags: Search tags
            **extra: Additional metadata
        """
        self.name = name
        self.namespace = namespace
        self.svg_content = svg_content.strip()
        self.category = category
        self.tags = tags or []
        self.extra = extra

    @property
    def qualified_name(self) -> str:
        """
        Full name with namespace.

        Returns:
            "namespace:name" or just "name" if no namespace
        """
        if self.namespace:
            return f"{self.namespace}:{self.name}"
        return self.name

    def render(
        self,
        size: int | None = None,
        width: int | None = None,
        height: int | None = None,
        css_class: str = "",
        color: str = "",
        fill: str = "",
        stroke: str = "",
        aria_label: str = "",
        aria_hidden: bool | None = None,
        **attrs: Any,
    ) -> SafeString:
        """
        Render the SVG with optional modifications.

        Args:
            size: Set both width and height (in pixels)
            width: Width in pixels (overrides size)
            height: Height in pixels (overrides size)
            css_class: CSS class(es) to add
            color: CSS color value (sets currentColor context)
            fill: SVG fill color
            stroke: SVG stroke color
            aria_label: Accessibility label (sets role="img")
            aria_hidden: Hide from screen readers (default True unless aria_label)
            **attrs: Additional HTML attributes (underscores become dashes)

        Returns:
            Safe HTML string with the rendered SVG
        """
        svg = self.svg_content

        # Find the opening <svg tag
        svg_match = self._SVG_TAG_PATTERN.search(svg)
        if not svg_match:
            return mark_safe("")

        tag_attrs = svg_match.group(1)

        # Handle size - use default if not specified
        if size is None and width is None and height is None:
            from .conf import get_setting

            default_size = get_setting("DEFAULT_SIZE")
            if default_size:
                size = default_size

        if size is not None:
            width = width or size
            height = height or size

        if width is not None:
            tag_attrs = self._WIDTH_PATTERN.sub("", tag_attrs)
            tag_attrs = f'{tag_attrs} width="{width}"'

        if height is not None:
            tag_attrs = self._HEIGHT_PATTERN.sub("", tag_attrs)
            tag_attrs = f'{tag_attrs} height="{height}"'

        # Handle CSS class - add default class if configured
        from .conf import get_setting

        default_class = get_setting("DEFAULT_CLASS")
        if default_class:
            css_class = f"{default_class} {css_class}".strip() if css_class else default_class

        if css_class:
            class_match = self._CLASS_PATTERN.search(tag_attrs)
            if class_match:
                existing = class_match.group(1)
                tag_attrs = tag_attrs.replace(
                    class_match.group(0),
                    f'class="{existing} {escape(css_class)}"',
                )
            else:
                tag_attrs = f'{tag_attrs} class="{escape(css_class)}"'

        # Handle colors
        style_parts = []
        if color:
            style_parts.append(f"color: {escape(color)}")

        # Handle fill - use default if not specified
        if not fill:
            default_fill = get_setting("DEFAULT_FILL")
            if default_fill:
                fill = default_fill

        if fill:
            # Remove existing fill and add new one
            tag_attrs = self._FILL_PATTERN.sub("", tag_attrs)
            tag_attrs = f'{tag_attrs} fill="{escape(fill)}"'
        if stroke:
            tag_attrs = f'{tag_attrs} stroke="{escape(stroke)}"'

        if style_parts:
            style_attr = "; ".join(style_parts)
            tag_attrs = f'{tag_attrs} style="{style_attr}"'

        # Handle ARIA
        if aria_label:
            tag_attrs = f'{tag_attrs} aria-label="{escape(aria_label)}" role="img"'
            # Don't hide if we have a label
            if aria_hidden is None:
                aria_hidden = False

        # Default to hidden if no label
        if aria_hidden is None:
            from .conf import get_setting

            aria_hidden = get_setting("ARIA_HIDDEN")

        if aria_hidden:
            tag_attrs = f'{tag_attrs} aria-hidden="true"'

        # Handle additional attributes
        for key, value in attrs.items():
            if value is None:
                continue
            # Convert underscores to dashes (data_id -> data-id)
            attr_name = key.replace("_", "-")
            tag_attrs = f'{tag_attrs} {attr_name}="{escape(str(value))}"'

        # Reconstruct SVG
        svg = svg.replace(svg_match.group(0), f"<svg{tag_attrs}>")
        return mark_safe(svg)

    def __str__(self) -> str:
        """Render icon with default settings."""
        return self.render()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"Icon({self.qualified_name!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on qualified name."""
        if isinstance(other, Icon):
            return self.qualified_name == other.qualified_name
        return False

    def __hash__(self) -> int:
        """Hash based on qualified name."""
        return hash(self.qualified_name)
