"""
Heroicons icon pack for djicons.

Beautiful hand-crafted SVG icons, by the makers of Tailwind CSS.
https://heroicons.com

Includes three styles:
- outline: 24x24, 1.5px stroke
- solid: 24x24, filled
- mini: 20x20, filled

Usage:
    from djicons import icons
    from djicons.packs import heroicons

    heroicons.register(icons)

    # Then use in templates:
    {% icon "hero:home" %}
    {% icon "hero:pencil-square" size=24 %}
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "hero"
VERSION = "2.2.0"
LICENSE = "MIT"
HOMEPAGE = "https://heroicons.com"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Heroicons pack with the registry.

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
        "name": "Heroicons",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
    }
