"""
Icon registry - Thread-safe singleton for managing icons.

The registry is the heart of djicons. It manages all icons across namespaces
and provides lazy-loading via loaders.

Usage:
    from djicons import icons

    # Get an icon
    icon = icons.get("ion:home")

    # Register a custom icon
    icons.register("my-icon", "<svg>...</svg>", namespace="myapp")

    # Register a loader for lazy loading
    from djicons.loaders import DirectoryIconLoader
    icons.register_loader(DirectoryIconLoader("/path/to/icons"), namespace="custom")
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .icon import Icon
    from .loaders.base import BaseIconLoader


class IconRegistry:
    """
    Thread-safe singleton registry for managing icons.

    Icons are organized by namespace:
    - "" (empty): core icons, global namespace
    - "ion": Ionicons
    - "hero": Heroicons
    - "material": Material Symbols
    - "tabler": Tabler Icons
    - "lucide": Lucide Icons
    - "inventory": ERPlora inventory module
    - "pos.sales": ERPlora POS sales submodule

    The registry supports:
    - Direct icon registration with SVG content
    - Lazy loading via registered loaders
    - Aliases for semantic naming
    - Thread-safe access
    """

    _instance: Optional["IconRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "IconRegistry":
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize registry state."""
        self._icons: dict[str, dict[str, "Icon"]] = {}  # namespace -> {name: Icon}
        self._loaders: dict[str, "BaseIconLoader"] = {}  # namespace -> loader
        self._aliases: dict[str, str] = {}  # alias -> "namespace:name"
        self._default_namespace: str = ""

    @property
    def default_namespace(self) -> str:
        """Get the default namespace."""
        return self._default_namespace

    @default_namespace.setter
    def default_namespace(self, value: str) -> None:
        """Set the default namespace."""
        self._default_namespace = value

    def register(
        self,
        name: str,
        svg_content: str,
        namespace: str = "",
        **metadata: str | list[str],
    ) -> "Icon":
        """
        Register an icon with optional metadata.

        Args:
            name: Icon identifier (e.g., "home", "cart-outline")
            svg_content: Raw SVG content as string
            namespace: Namespace for the icon (e.g., "ion", "myapp")
            **metadata: Additional metadata (category, tags, etc.)

        Returns:
            The registered Icon instance
        """
        from .icon import Icon

        if namespace not in self._icons:
            self._icons[namespace] = {}

        icon = Icon(
            name=name,
            svg_content=svg_content,
            namespace=namespace,
            **metadata,
        )
        self._icons[namespace][name] = icon
        return icon

    def register_loader(self, loader: "BaseIconLoader", namespace: str = "") -> None:
        """
        Register a loader for lazy-loading icons in a namespace.

        Loaders are used when an icon is requested but not yet registered.
        The loader will be called to load the icon from its source.

        Args:
            loader: Icon loader instance
            namespace: Namespace for the loader
        """
        self._loaders[namespace] = loader

    def register_alias(self, alias: str, target: str) -> None:
        """
        Create an alias for an icon.

        Aliases allow semantic naming of icons that can be changed
        without updating templates.

        Example:
            icons.register_alias("edit", "hero:pencil")
            icons.register_alias("delete", "hero:trash")
            icons.get("edit")  # Returns hero:pencil

        Args:
            alias: Alias name
            target: Target icon in "namespace:name" format
        """
        self._aliases[alias] = target

    def get(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Optional["Icon"]:
        """
        Get an icon by name.

        Supports multiple formats:
        - "home" -> looks in default namespace
        - "ion:home" -> explicit namespace
        - "inventory.products" -> module namespace with dot notation

        Args:
            name: Icon name, optionally prefixed with namespace
            namespace: Override namespace (if not in name)

        Returns:
            Icon instance or None if not found
        """
        # Check aliases first
        if name in self._aliases:
            name = self._aliases[name]

        # Parse namespace from name
        if ":" in name and namespace is None:
            namespace, name = name.split(":", 1)

        # Use default namespace if none specified
        if namespace is None:
            from .conf import get_setting

            namespace = get_setting("DEFAULT_NAMESPACE") or self._default_namespace

        # Try to get from registered icons
        if namespace in self._icons and name in self._icons[namespace]:
            return self._icons[namespace][name]

        # Try lazy loading via loader
        if namespace in self._loaders:
            loader = self._loaders[namespace]
            svg_content = loader.load(name)
            if svg_content:
                return self.register(name, svg_content, namespace)

        # Not found
        return None

    def has(self, name: str, namespace: Optional[str] = None) -> bool:
        """
        Check if an icon exists.

        Args:
            name: Icon name, optionally prefixed with namespace
            namespace: Override namespace

        Returns:
            True if icon exists or can be loaded
        """
        return self.get(name, namespace) is not None

    def list_icons(self, namespace: Optional[str] = None) -> list[str]:
        """
        List all registered icons, optionally filtered by namespace.

        Args:
            namespace: Filter by namespace (None for all)

        Returns:
            List of icon names (with namespace prefix if multiple namespaces)
        """
        if namespace is not None:
            return sorted(self._icons.get(namespace, {}).keys())

        result = []
        for ns, icons_dict in self._icons.items():
            prefix = f"{ns}:" if ns else ""
            result.extend(f"{prefix}{name}" for name in icons_dict.keys())
        return sorted(result)

    def list_namespaces(self) -> list[str]:
        """
        List all registered namespaces.

        Returns:
            List of namespace names
        """
        return sorted(set(self._icons.keys()) | set(self._loaders.keys()))

    def clear(self, namespace: Optional[str] = None) -> None:
        """
        Clear registered icons.

        Args:
            namespace: Clear only this namespace (None for all)
        """
        if namespace is not None:
            self._icons.pop(namespace, None)
        else:
            self._icons.clear()

    def __contains__(self, name: str) -> bool:
        """Check if icon exists (for 'in' operator)."""
        return self.has(name)

    def __len__(self) -> int:
        """Return total number of registered icons."""
        return sum(len(icons_dict) for icons_dict in self._icons.values())


# Global registry instance
icons = IconRegistry()
