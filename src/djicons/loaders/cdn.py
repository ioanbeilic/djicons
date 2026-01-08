"""
CDN icon loader - Load SVG files from CDN URLs.

This loader fetches icons from CDN in development mode,
avoiding the need to download all icons locally.

Usage:
    from djicons.loaders import CDNIconLoader
    from djicons import icons

    loader = CDNIconLoader(
        base_url="https://unpkg.com/ionicons@7.4.0/dist/svg/{name}.svg",
        namespace="ion"
    )
    icons.register_loader(loader, namespace="ion")

    # Icons are fetched from CDN when requested
    icon = icons.get("ion:home")  # Fetches from CDN
"""

import logging
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from .base import BaseIconLoader

logger = logging.getLogger(__name__)


# CDN URL templates for each icon pack
CDN_TEMPLATES = {
    "ion": "https://unpkg.com/ionicons@7.4.0/dist/svg/{name}.svg",
    "hero": "https://unpkg.com/heroicons@2.2.0/24/outline/{name}.svg",
    "tabler": "https://unpkg.com/@tabler/icons@3.28.1/icons/outline/{name}.svg",
    "lucide": "https://unpkg.com/lucide-static@0.469.0/icons/{name}.svg",
    "fa": "https://unpkg.com/@fortawesome/fontawesome-free@6.7.2/svgs/solid/{name}.svg",
    "material": "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{name}/default/24px.svg",
}


class CDNIconLoader(BaseIconLoader):
    """
    Load icons from CDN URLs.

    This loader is designed for development mode where you want
    access to all icons without downloading them locally.

    Features:
    - Lazy loading from CDN
    - In-memory caching
    - Fallback support
    - Timeout handling
    """

    def __init__(
        self,
        namespace: str,
        base_url: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        """
        Initialize CDN loader.

        Args:
            namespace: Icon pack namespace (e.g., 'ion', 'hero')
            base_url: URL template with {name} placeholder. If None, uses built-in template.
            timeout: HTTP request timeout in seconds
        """
        self.namespace = namespace
        self.base_url = base_url or CDN_TEMPLATES.get(namespace)
        self.timeout = timeout
        self._cache: dict[str, str] = {}
        self._failed: set[str] = set()  # Track failed fetches to avoid retrying

        if not self.base_url:
            raise ValueError(
                f"No CDN URL template for namespace '{namespace}'. "
                f"Available: {list(CDN_TEMPLATES.keys())}. "
                f"Or provide a custom base_url."
            )

    def load(self, name: str) -> str | None:
        """
        Load SVG content from CDN.

        Args:
            name: Icon name

        Returns:
            SVG content as string, or None if not found
        """
        # Check memory cache first
        if name in self._cache:
            return self._cache[name]

        # Skip if previously failed
        if name in self._failed:
            return None

        url = self.base_url.format(name=name)

        try:
            with urlopen(url, timeout=self.timeout) as response:
                content = response.read().decode("utf-8")
                self._cache[name] = content
                return content
        except HTTPError as e:
            if e.code == 404:
                logger.debug(f"Icon not found on CDN: {name} ({url})")
            else:
                logger.warning(f"HTTP error fetching icon {name}: {e.code}")
            self._failed.add(name)
            return None
        except URLError as e:
            logger.warning(f"Network error fetching icon {name}: {e.reason}")
            self._failed.add(name)
            return None
        except Exception as e:
            logger.error(f"Error fetching icon {name}: {e}")
            self._failed.add(name)
            return None

    def list(self) -> list[str]:
        """
        List cached icon names.

        Note: CDN loaders cannot list all available icons.
        Only returns icons that have been loaded.

        Returns:
            List of cached icon names
        """
        return sorted(self._cache.keys())

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()
        self._failed.clear()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"CDNIconLoader({self.namespace!r}, {self.base_url!r})"
