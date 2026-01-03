"""
Font Awesome Free icon pack for djicons.

Font Awesome is the web's most popular icon set and toolkit.
https://fontawesome.com

Includes three styles (Free version):
- solid: Filled icons
- regular: Outlined icons
- brands: Brand logos

Usage:
    from djicons import icons
    from djicons.packs import fontawesome

    fontawesome.register(icons)

    # Then use in templates:
    {% icon "fa:house" %}              {# solid (default) #}
    {% icon "fa:heart-regular" %}      {# regular style #}
    {% icon "fa:github-brands" %}      {# brand icon #}

License Note:
    Font Awesome Free icons are available under:
    - Icons: CC BY 4.0 License
    - Fonts: SIL OFL 1.1 License
    - Code: MIT License

    You must include attribution when using Font Awesome icons.
    See: https://fontawesome.com/license/free
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...registry import IconRegistry

NAMESPACE = "fa"
VERSION = "6.7.2"
LICENSE = "CC BY 4.0 / MIT"
HOMEPAGE = "https://fontawesome.com"

ICONS_DIR = Path(__file__).parent / "icons"


def register(registry: "IconRegistry") -> None:
    """
    Register Font Awesome pack with the registry.

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
        "name": "Font Awesome Free",
        "namespace": NAMESPACE,
        "version": VERSION,
        "license": LICENSE,
        "homepage": HOMEPAGE,
        "count": icon_count,
        "installed": ICONS_DIR.exists() and icon_count > 0,
        "attribution_required": True,
    }
