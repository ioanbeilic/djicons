"""Django app configuration for djicons."""

from pathlib import Path

from django.apps import AppConfig

# Mapping from pack names to namespaces
PACK_NAMESPACES = {
    "ionicons": "ion",
    "heroicons": "hero",
    "material": "material",
    "tabler": "tabler",
    "lucide": "lucide",
    "fontawesome": "fa",
}


class DjiconsConfig(AppConfig):
    """Django app configuration for djicons."""

    name = "djicons"
    verbose_name = "Django Icons"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Initialize djicons when Django starts."""
        from .conf import get_setting
        from .registry import icons

        mode = get_setting("MODE")

        # Register custom icon directories from settings (highest priority)
        self._register_icon_dirs()

        # Auto-discover and register icon packs based on mode
        if get_setting("AUTO_DISCOVER"):
            if mode == "cdn":
                self._register_cdn_loaders()
            else:
                # Check for collected icons first, then fall back to packs
                collect_dir = get_setting("COLLECT_DIR")
                if collect_dir and Path(collect_dir).exists():
                    self._register_collected_icons(collect_dir)
                else:
                    self._register_packs()

        # Register aliases from settings
        aliases = get_setting("ALIASES")
        for alias, target in aliases.items():
            icons.register_alias(alias, target)

    def _register_icon_dirs(self) -> None:
        """Register custom icon directories from ICON_DIRS setting."""
        from .conf import get_setting
        from .loaders import DirectoryIconLoader
        from .registry import icons

        icon_dirs = get_setting("ICON_DIRS") or {}

        for namespace, path in icon_dirs.items():
            icon_path = Path(path) if isinstance(path, str) else path
            if icon_path.exists():
                loader = DirectoryIconLoader(icon_path)
                icons.register_loader(loader, namespace=namespace)

    def _register_cdn_loaders(self) -> None:
        """Register CDN loaders for all configured packs."""
        from .conf import get_setting
        from .loaders import CDNIconLoader
        from .registry import icons

        packs = get_setting("PACKS")

        for pack_name in packs:
            namespace = PACK_NAMESPACES.get(pack_name)
            if namespace:
                try:
                    loader = CDNIconLoader(namespace=namespace)
                    icons.register_loader(loader, namespace=namespace)
                except ValueError:
                    # No CDN template for this pack
                    pass

    def _register_collected_icons(self, collect_dir: str | Path) -> None:
        """Register collected icons from COLLECT_DIR."""
        from .loaders import DirectoryIconLoader
        from .registry import icons

        collect_path = Path(collect_dir)

        # Each namespace has its own subdirectory
        for namespace_dir in collect_path.iterdir():
            if namespace_dir.is_dir():
                namespace = namespace_dir.name
                loader = DirectoryIconLoader(namespace_dir)
                icons.register_loader(loader, namespace=namespace)

    def _register_packs(self) -> None:
        """Register configured icon packs (local mode with downloaded icons)."""
        from .conf import get_setting
        from .registry import icons

        packs = get_setting("PACKS")

        for pack_name in packs:
            try:
                if pack_name == "ionicons":
                    from .packs.ionicons import register

                    register(icons)
                elif pack_name == "heroicons":
                    from .packs.heroicons import register

                    register(icons)
                elif pack_name == "material":
                    from .packs.material import register

                    register(icons)
                elif pack_name == "tabler":
                    from .packs.tabler import register

                    register(icons)
                elif pack_name == "lucide":
                    from .packs.lucide import register

                    register(icons)
                elif pack_name == "fontawesome":
                    from .packs.fontawesome import register

                    register(icons)
            except ImportError:
                # Pack not available (icons not downloaded yet)
                pass
