"""
Built-in icon packs for djicons.

Available packs:
- ionicons: Ionicons 7.x (~1400 icons)
- heroicons: Heroicons 2.x (~300 icons)
- material: Material Symbols (~2500 icons)
- tabler: Tabler Icons (~5000 icons)
- lucide: Lucide Icons (~1500 icons)

Each pack provides:
- register(registry): Function to register the pack with a registry
- NAMESPACE: The namespace prefix for the pack
- VERSION: Version of the icon library
- LICENSE: License of the icon library

Usage:
    from djicons import icons
    from djicons.packs import ionicons

    ionicons.register(icons)
    icon = icons.get("ion:home")
"""

from pathlib import Path

PACKS_DIR = Path(__file__).parent


def get_pack_path(pack_name: str) -> Path:
    """Get the path to a pack's icons directory."""
    return PACKS_DIR / pack_name / "icons"


def list_available_packs() -> list[str]:
    """List all available packs."""
    packs = []
    for path in PACKS_DIR.iterdir():
        if path.is_dir() and (path / "__init__.py").exists():
            packs.append(path.name)
    return sorted(packs)
