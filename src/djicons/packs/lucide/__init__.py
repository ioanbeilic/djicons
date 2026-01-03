"""
Lucide Icons pack for djicons.

Beautiful & consistent icons. A fork of Feather Icons with more icons.
https://lucide.dev

Usage:
    from djicons import icons
    from djicons.packs import lucide

    lucide.register(icons)

    # Then use in templates:
    {% icon "lucide:home" %}
    {% icon "lucide:shopping-cart" size=24 %}
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "lucide"
VERSION = "0.469.0"
LICENSE = "ISC"
HOMEPAGE = "https://lucide.dev"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Lucide Icons pack with the registry.

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
        "name": "Lucide Icons",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
    }
