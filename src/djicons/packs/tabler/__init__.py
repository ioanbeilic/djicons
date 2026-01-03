"""
Tabler Icons pack for djicons.

Over 5000 free MIT-licensed SVG icons for web projects.
https://tabler.io/icons

Usage:
    from djicons import icons
    from djicons.packs import tabler

    tabler.register(icons)

    # Then use in templates:
    {% icon "tabler:home" %}
    {% icon "tabler:shopping-cart" size=24 %}
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "tabler"
VERSION = "3.28.1"
LICENSE = "MIT"
HOMEPAGE = "https://tabler.io/icons"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Tabler Icons pack with the registry.

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
        "name": "Tabler Icons",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
    }
