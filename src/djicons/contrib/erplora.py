"""
ERPlora module integration for djicons.

This module provides automatic icon registration for ERPlora modules.
Each module can have custom icons in its static/icons/ directory.

Usage in module's apps.py:
    from django.apps import AppConfig

    class InventoryConfig(AppConfig):
        name = 'inventory'

        def ready(self):
            from djicons.contrib.erplora import register_module_icons
            register_module_icons(self.name, self.path)

Or auto-discover all modules:
    from djicons.contrib.erplora import discover_module_icons
    discover_module_icons("/path/to/modules")
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..registry import IconRegistry


def register_module_icons(
    module_id: str,
    module_path: str | Path,
    registry: "IconRegistry | None" = None,
) -> int:
    """
    Register icons for an ERPlora module.

    Looks for icons in:
    1. {module_path}/static/icons/icon.svg (main module icon)
    2. {module_path}/static/icons/*.svg (additional icons)

    Icons are registered in the namespace matching the module_id.

    Args:
        module_id: Module identifier (e.g., "inventory", "sales")
        module_path: Absolute path to module directory
        registry: Icon registry (uses global if not provided)

    Returns:
        Number of icons registered
    """
    if registry is None:
        from ..registry import icons

        registry = icons

    from ..loaders import DirectoryIconLoader

    icons_dir = Path(module_path) / "static" / "icons"

    if not icons_dir.exists():
        return 0

    # Register directory loader for lazy loading
    loader = DirectoryIconLoader(icons_dir)
    registry.register_loader(loader, namespace=module_id)

    # Pre-register main module icon if it exists
    main_icon = icons_dir / "icon.svg"
    if main_icon.exists():
        try:
            svg_content = main_icon.read_text(encoding="utf-8")
            registry.register(
                name="icon",
                svg_content=svg_content,
                namespace=module_id,
                category="module",
            )
        except (OSError, UnicodeDecodeError):
            pass

    # Count available icons
    return len(list(icons_dir.glob("*.svg")))


def discover_module_icons(
    modules_dir: str | Path,
    registry: "IconRegistry | None" = None,
) -> dict[str, int]:
    """
    Automatically discover and register icons for all ERPlora modules.

    Scans the modules directory for subdirectories with static/icons/ folders
    and registers their icons.

    Args:
        modules_dir: Path to ERPlora modules directory
        registry: Icon registry (uses global if not provided)

    Returns:
        Dictionary mapping module_id to icon count
    """
    if registry is None:
        from ..registry import icons

        registry = icons

    modules_path = Path(modules_dir)
    results: dict[str, int] = {}

    if not modules_path.exists():
        return results

    for module_dir in modules_path.iterdir():
        if not module_dir.is_dir():
            continue

        # Get module name (skip hidden directories, handle prefixes)
        name = module_dir.name
        if name.startswith("."):
            continue

        # Handle disabled modules (prefixed with _)
        if name.startswith("_"):
            name = name[1:]

        icons_dir = module_dir / "static" / "icons"
        if icons_dir.exists():
            count = register_module_icons(name, module_dir, registry)
            if count > 0:
                results[name] = count

    return results


def get_module_icon(
    module_id: str,
    fallback: str = "ion:cube-outline",
    size: int | None = None,
    css_class: str = "",
) -> str:
    """
    Get the rendered icon for a module.

    Priority:
    1. Custom SVG from module's static/icons/icon.svg
    2. Fallback icon (default: ion:cube-outline)

    Args:
        module_id: Module identifier
        fallback: Fallback icon name (with namespace)
        size: Icon size in pixels
        css_class: CSS classes to add

    Returns:
        Rendered SVG HTML string
    """
    from ..registry import icons

    # Try module's custom icon
    icon = icons.get("icon", namespace=module_id)
    if icon:
        return icon.render(size=size, css_class=css_class)

    # Fallback
    fallback_icon = icons.get(fallback)
    if fallback_icon:
        return fallback_icon.render(size=size, css_class=css_class)

    return ""


def setup_erplora_icons(
    modules_dir: str | Path,
    ionicons_dir: str | Path | None = None,
) -> None:
    """
    Complete setup for ERPlora icon system.

    This function:
    1. Registers Ionicons from the Hub's static directory
    2. Discovers and registers module icons

    Call this in Django settings or a ready() method.

    Args:
        modules_dir: Path to ERPlora modules directory
        ionicons_dir: Path to Ionicons SVG directory (optional)
    """
    from ..loaders import DirectoryIconLoader
    from ..registry import icons

    # Register Ionicons if path provided
    if ionicons_dir:
        ionicons_path = Path(ionicons_dir)
        if ionicons_path.exists():
            loader = DirectoryIconLoader(ionicons_path)
            icons.register_loader(loader, namespace="ion")

    # Discover module icons
    discover_module_icons(modules_dir, icons)
