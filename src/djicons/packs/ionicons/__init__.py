"""
Ionicons icon pack for djicons.

Ionicons is a premium icon pack with 1400+ icons for web, iOS, Android, and desktop apps.
https://ionicons.com

Usage:
    from djicons import icons
    from djicons.packs import ionicons

    ionicons.register(icons)

    # Then use in templates:
    {% icon "ion:home" %}
    {% icon "ion:cart-outline" size=24 %}
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "ion"
VERSION = "7.4.0"
LICENSE = "MIT"
HOMEPAGE = "https://ionicons.com"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Ionicons pack with the registry.

    Args:
        registry: The icon registry to register with
    """
    from ...loaders import DirectoryIconLoader

    if ICONS_DIR.exists():
        loader = DirectoryIconLoader(ICONS_DIR)
        registry.register_loader(loader, namespace=NAMESPACE)


def get_metadata() -> dict:
    """Return pack metadata."""
    icon_count = len(list(ICONS_DIR.glob("*.svg"))) if ICONS_DIR.exists() else 0
    return {
        "name": "Ionicons",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
    }
