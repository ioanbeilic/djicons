"""
Icon loaders for djicons.

Loaders provide lazy-loading of icons from various sources.

Available loaders:
    - DirectoryIconLoader: Load SVG files from a directory
    - CDNIconLoader: Load SVG files from CDN (for development)
    - BaseIconLoader: Abstract base class for custom loaders
"""

from .base import BaseIconLoader
from .cdn import CDNIconLoader
from .directory import DirectoryIconLoader

__all__ = [
    "BaseIconLoader",
    "CDNIconLoader",
    "DirectoryIconLoader",
]
