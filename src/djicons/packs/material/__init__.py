"""
Material Symbols icon pack for djicons.

Material Symbols are Google's newest icons consolidating over 2,500 glyphs
in a single font file with a wide range of design variants.
https://fonts.google.com/icons

Usage:
    from djicons import icons
    from djicons.packs import material

    material.register(icons)

    # Then use in templates:
    {% icon "material:home" %}
    {% icon "material:shopping_cart" size=24 %}
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "material"
VERSION = "latest"
LICENSE = "Apache-2.0"
HOMEPAGE = "https://fonts.google.com/icons"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Material Symbols pack with the registry.

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
        "name": "Material Symbols",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
    }
