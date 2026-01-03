"""
Icon loaders for djicons.

Loaders provide lazy-loading of icons from various sources.

Available loaders:
    - DirectoryIconLoader: Load SVG files from a directory
    - BaseIconLoader: Abstract base class for custom loaders
"""

from .base import BaseIconLoader
from .directory import DirectoryIconLoader

__all__ = [
    "BaseIconLoader",
    "DirectoryIconLoader",
]
