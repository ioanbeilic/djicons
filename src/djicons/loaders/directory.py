"""
Directory icon loader - Load SVG files from a directory.

Usage:
    from djicons.loaders import DirectoryIconLoader
    from djicons import icons

    loader = DirectoryIconLoader("/path/to/icons")
    icons.register_loader(loader, namespace="myapp")

    # Icons are loaded lazily when requested
    icon = icons.get("myapp:home")  # Loads /path/to/icons/home.svg
"""

from functools import lru_cache
from pathlib import Path

from .base import BaseIconLoader


class DirectoryIconLoader(BaseIconLoader):
    """
    Load icons from a directory of SVG files.

    Expected structure:
        icons/
        ├── home.svg
        ├── home-outline.svg
        ├── cart.svg
        └── ...

    Supports:
    - Flat directory structure
    - Recursive scanning (optional)
    - Custom file extensions
    - LRU caching of loaded icons
    """

    def __init__(
        self,
        directory: str | Path,
        extension: str = ".svg",
        recursive: bool = False,
    ) -> None:
        """
        Initialize directory loader.

        Args:
            directory: Path to directory containing SVG files
            extension: File extension to look for (default: .svg)
            recursive: Whether to scan subdirectories
        """
        self.directory = Path(directory)
        self.extension = extension
        self.recursive = recursive
        self._cache: dict[str, str] = {}

    @lru_cache(maxsize=1)
    def _scan_directory(self) -> dict[str, Path]:
        """
        Scan directory and build name -> path mapping.

        Returns:
            Dictionary mapping icon names to file paths
        """
        icons: dict[str, Path] = {}

        if not self.directory.exists():
            return icons

        pattern = f"**/*{self.extension}" if self.recursive else f"*{self.extension}"

        for path in self.directory.glob(pattern):
            if path.is_file():
                name = path.stem  # filename without extension
                icons[name] = path

        return icons

    def load(self, name: str) -> str | None:
        """
        Load SVG content by icon name.

        Args:
            name: Icon name (filename without extension)

        Returns:
            SVG content as string, or None if not found
        """
        # Check memory cache first
        if name in self._cache:
            return self._cache[name]

        icons = self._scan_directory()

        if name not in icons:
            return None

        try:
            content = icons[name].read_text(encoding="utf-8")
            self._cache[name] = content
            return content
        except (OSError, UnicodeDecodeError):
            return None

    def list(self) -> list[str]:
        """
        List all available icon names.

        Returns:
            Sorted list of icon names
        """
        return sorted(self._scan_directory().keys())

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        self._scan_directory.cache_clear()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"DirectoryIconLoader({self.directory!r})"
