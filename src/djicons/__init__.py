"""
djicons - Multi-library SVG icon system for Django.

Like react-icons, but 100% backend-driven. No CDN, no JavaScript, offline-first.

Basic Usage:
    {% load djicons %}
    {% icon "home" %}
    {% icon "ion:cart-outline" size=24 %}
    {% icon "hero:pencil" css_class="text-primary" %}

Programmatic Usage:
    from djicons import icons, Icon

    # Get an icon
    icon = icons.get("ion:home")
    html = icon.render(size=24, css_class="text-primary")

    # Register custom icons
    icons.register("my-icon", svg_content, namespace="myapp")

    # Register a loader for a directory
    from djicons.loaders import DirectoryIconLoader
    icons.register_loader(
        DirectoryIconLoader("/path/to/icons"),
        namespace="custom"
    )

Supported Icon Packs:
    - ion: Ionicons 7.x (~1400 icons)
    - hero: Heroicons 2.x (~300 icons)
    - material: Material Symbols (~2500 icons)
    - tabler: Tabler Icons (~4000 icons)
    - lucide: Lucide Icons (~1000 icons)
"""

__version__ = "0.2.0"
__author__ = "Ioan Beilic"
__email__ = "ioanbeilic@gmail.com"

# Core classes
from .icon import Icon

# Loaders
from .loaders.base import BaseIconLoader
from .loaders.directory import DirectoryIconLoader
from .registry import IconRegistry, icons

__all__ = [
    # Version
    "__version__",
    # Classes
    "Icon",
    "IconRegistry",
    "BaseIconLoader",
    "DirectoryIconLoader",
    # Instances
    "icons",
    # Functions
    "get",
    "register",
]


def get(name: str, **kwargs) -> str:
    """
    Get and render an icon by name.

    Shortcut for: icons.get(name).render(**kwargs)

    Args:
        name: Icon name, optionally with namespace (e.g., "ion:home")
        **kwargs: Render options (size, css_class, color, etc.)

    Returns:
        Rendered SVG HTML string, or empty string if not found
    """
    icon = icons.get(name)
    if icon:
        return icon.render(**kwargs)
    return ""


def register(name: str, svg_content: str, namespace: str = "", **metadata) -> Icon:
    """
    Register an icon.

    Shortcut for: icons.register(name, svg_content, namespace, **metadata)

    Args:
        name: Icon identifier
        svg_content: Raw SVG content
        namespace: Namespace for the icon (e.g., "myapp")
        **metadata: Additional metadata (category, tags, etc.)

    Returns:
        The registered Icon instance
    """
    return icons.register(name, svg_content, namespace, **metadata)
