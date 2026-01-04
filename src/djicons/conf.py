"""Configuration settings for djicons."""

from typing import Any

from django.conf import settings

# Default settings
DEFAULTS: dict[str, Any] = {
    # Default namespace for unqualified icon names
    "DEFAULT_NAMESPACE": "ion",
    # Auto-discover and register installed packs
    "AUTO_DISCOVER": True,
    # Return empty string for missing icons (vs raising error)
    "MISSING_ICON_SILENT": True,
    # Use Django cache backend in addition to memory cache
    "USE_DJANGO_CACHE": False,
    # Cache timeout in seconds (24 hours)
    "CACHE_TIMEOUT": 86400,
    # Max icons in memory LRU cache
    "MEMORY_CACHE_SIZE": 1000,
    # Default icon size (None = use SVG's native size)
    "DEFAULT_SIZE": None,
    # Default CSS class to add to all icons
    "DEFAULT_CLASS": "",
    # Add aria-hidden="true" by default
    "ARIA_HIDDEN": True,
    # Icon packs to auto-load
    "PACKS": [
        "ionicons",
        "heroicons",
        "material",
        "tabler",
        "lucide",
        "fontawesome",
    ],
    # Custom icon directories by namespace
    # Example: {"ion": "/path/to/ionicons/svg", "custom": "/app/static/icons"}
    "ICON_DIRS": {},
    # Aliases for common icons (alias -> "namespace:name")
    "ALIASES": {},
}


def get_setting(name: str) -> Any:
    """
    Get a djicons setting with fallback to default.

    Settings can be configured in Django settings as:
        DJICONS = {
            'DEFAULT_NAMESPACE': 'hero',
            'PACKS': ['heroicons', 'ionicons'],
        }

    Or as individual settings:
        DJICONS_DEFAULT_NAMESPACE = 'hero'
        DJICONS_PACKS = ['heroicons', 'ionicons']

    Args:
        name: Setting name without DJICONS_ prefix

    Returns:
        Setting value
    """
    # First check DJICONS dict
    djicons_settings = getattr(settings, "DJICONS", {})
    if name in djicons_settings:
        return djicons_settings[name]

    # Then check individual settings
    full_name = f"DJICONS_{name}"
    if hasattr(settings, full_name):
        return getattr(settings, full_name)

    # Return default
    return DEFAULTS.get(name)
