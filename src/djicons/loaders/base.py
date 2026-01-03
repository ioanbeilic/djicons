"""
Base icon loader abstract class.

Loaders provide lazy-loading of icons from various sources.
Implement this class to create custom loaders.

Example:
    class MyApiLoader(BaseIconLoader):
        def load(self, name: str) -> str | None:
            response = requests.get(f"https://api.example.com/icons/{name}.svg")
            if response.ok:
                return response.text
            return None

        def list(self) -> list[str]:
            response = requests.get("https://api.example.com/icons/")
            return response.json()["icons"]
"""

from abc import ABC, abstractmethod


class BaseIconLoader(ABC):
    """
    Abstract base class for icon loaders.

    Loaders provide lazy-loading of icons from various sources:
    - Filesystem directories
    - JSON/YAML metadata files
    - Remote APIs
    - Python packages
    """

    @abstractmethod
    def load(self, name: str) -> str | None:
        """
        Load an icon by name.

        Args:
            name: Icon name (without namespace prefix)

        Returns:
            SVG content as string, or None if not found
        """
        pass

    @abstractmethod
    def list(self) -> list[str]:
        """
        List all available icon names.

        Returns:
            List of icon names that can be loaded
        """
        pass

    def __contains__(self, name: str) -> bool:
        """Check if icon exists (for 'in' operator)."""
        return name in self.list()
