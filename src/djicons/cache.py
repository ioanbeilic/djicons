"""
Caching layer for djicons.

Provides two-tier caching:
1. LRU in-memory cache (fast, per-process)
2. Django cache backend (optional, shared across processes)

Usage:
    from djicons.cache import icon_cache

    # Get cached rendered icon
    html = icon_cache.get("ion:home", size=24)

    # Cache a rendered icon
    icon_cache.set("ion:home", "<svg>...</svg>", size=24)
"""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Any

from django.core.cache import cache as django_cache


class IconCache:
    """
    Two-tier caching for rendered icon SVG content.

    Tier 1: LRU in-memory cache (fast, per-process)
    Tier 2: Django cache backend (optional, shared across processes)

    Cache keys format: "djicons:{namespace}:{name}:{param_hash}"
    The hash includes render parameters for unique caching of variants.
    """

    CACHE_PREFIX = "djicons"

    def __init__(
        self,
        use_django_cache: bool | None = None,
        memory_maxsize: int | None = None,
        timeout: int | None = None,
    ) -> None:
        """
        Initialize cache.

        Args:
            use_django_cache: Whether to use Django cache backend
            memory_maxsize: Max items in memory cache
            timeout: Cache timeout in seconds
        """
        from .conf import get_setting

        if use_django_cache is None:
            use_django_cache = get_setting("USE_DJANGO_CACHE")
        if memory_maxsize is None:
            memory_maxsize = get_setting("MEMORY_CACHE_SIZE")
        if timeout is None:
            timeout = get_setting("CACHE_TIMEOUT")

        self.use_django_cache = use_django_cache
        self.timeout = timeout
        self._memory_maxsize = memory_maxsize
        self._memory_cache: OrderedDict[str, str] = OrderedDict()

    def _make_key(
        self,
        name: str,
        namespace: str = "",
        render_params: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate cache key.

        Args:
            name: Icon name
            namespace: Icon namespace
            render_params: Render parameters to include in key

        Returns:
            Cache key string
        """
        parts = [self.CACHE_PREFIX, namespace, name]

        if render_params:
            # Sort params for consistent hashing
            param_str = str(sorted(render_params.items()))
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            parts.append(param_hash)

        return ":".join(filter(None, parts))

    def get(
        self,
        name: str,
        namespace: str = "",
        **render_params: Any,
    ) -> str | None:
        """
        Get cached rendered SVG content.

        Args:
            name: Icon name
            namespace: Icon namespace
            **render_params: Render parameters used to generate the cache key

        Returns:
            Cached SVG content or None
        """
        key = self._make_key(name, namespace, render_params if render_params else None)

        # Check memory cache first (and move to end for LRU)
        if key in self._memory_cache:
            self._memory_cache.move_to_end(key)
            return self._memory_cache[key]

        # Check Django cache
        if self.use_django_cache:
            value = django_cache.get(key)
            if value is not None:
                # Populate memory cache
                self._memory_set(key, value)
                return value

        return None

    def _memory_set(self, key: str, value: str) -> None:
        """Set value in memory cache with LRU eviction."""
        # Evict oldest if at capacity
        while len(self._memory_cache) >= self._memory_maxsize:
            self._memory_cache.popitem(last=False)

        self._memory_cache[key] = value
        self._memory_cache.move_to_end(key)

    def set(
        self,
        name: str,
        content: str,
        namespace: str = "",
        **render_params: Any,
    ) -> None:
        """
        Cache rendered SVG content.

        Args:
            name: Icon name
            content: Rendered SVG content
            namespace: Icon namespace
            **render_params: Render parameters used to generate the cache key
        """
        key = self._make_key(name, namespace, render_params if render_params else None)

        self._memory_set(key, content)

        if self.use_django_cache:
            django_cache.set(key, content, self.timeout)

    def clear(self, namespace: str | None = None) -> None:
        """
        Clear cache.

        Args:
            namespace: Clear only this namespace (None for all)
        """
        if namespace is not None:
            prefix = f"{self.CACHE_PREFIX}:{namespace}:"
            keys_to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._memory_cache[key]
        else:
            self._memory_cache.clear()

    def stats(self) -> dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "memory_size": len(self._memory_cache),
            "memory_maxsize": self._memory_maxsize,
        }


# Global cache instance
icon_cache = IconCache()
