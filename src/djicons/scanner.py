"""
Template scanner for djicons.

Scans Django templates to find all icon usages and collect
only the icons that are actually used in the project.
"""

import re
from pathlib import Path

from django.conf import settings


# Regex patterns to match icon template tags
# Matches: {% icon "name" %}, {% icon 'name' %}, {% icon "ns:name" %}
ICON_PATTERN = re.compile(
    r'{%\s*icon\s+["\']([^"\']+)["\']',
    re.MULTILINE
)


def get_template_dirs() -> list[Path]:
    """
    Get all template directories from Django settings.

    Returns:
        List of template directory paths
    """
    template_dirs: list[Path] = []

    # Get from TEMPLATES setting
    templates_config = getattr(settings, 'TEMPLATES', [])
    for config in templates_config:
        # DIRS from each template backend
        for dir_path in config.get('DIRS', []):
            path = Path(dir_path)
            if path.exists():
                template_dirs.append(path)

        # APP_DIRS: scan each installed app's templates folder
        if config.get('APP_DIRS', False):
            for app in settings.INSTALLED_APPS:
                try:
                    # Get app path
                    module = __import__(app, fromlist=[''])
                    app_path = Path(module.__file__).parent
                    templates_path = app_path / 'templates'
                    if templates_path.exists():
                        template_dirs.append(templates_path)
                except (ImportError, AttributeError):
                    pass

    return template_dirs


def scan_file(file_path: Path) -> set[str]:
    """
    Scan a single template file for icon usages.

    Args:
        file_path: Path to the template file

    Returns:
        Set of icon names found (with namespace if specified)
    """
    icons = set()

    try:
        content = file_path.read_text(encoding='utf-8')
        matches = ICON_PATTERN.findall(content)
        icons.update(matches)
    except (OSError, UnicodeDecodeError):
        pass

    return icons


def scan_directory(directory: Path, extensions: tuple[str, ...] = ('.html', '.txt')) -> set[str]:
    """
    Scan a directory recursively for icon usages in templates.

    Args:
        directory: Directory to scan
        extensions: File extensions to scan

    Returns:
        Set of icon names found
    """
    icons = set()

    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            icons.update(scan_file(file_path))

    return icons


def scan_templates() -> set[str]:
    """
    Scan all Django templates for icon usages.

    Returns:
        Set of all icon names used in templates
    """
    icons = set()

    for template_dir in get_template_dirs():
        icons.update(scan_directory(template_dir))

    return icons


def parse_icon_name(name: str, default_namespace: str = 'ion') -> tuple[str, str]:
    """
    Parse an icon name into namespace and name.

    Args:
        name: Icon name (e.g., 'home', 'ion:home', 'hero:pencil')
        default_namespace: Default namespace if not specified

    Returns:
        Tuple of (namespace, icon_name)
    """
    if ':' in name:
        namespace, icon_name = name.split(':', 1)
        return namespace, icon_name
    return default_namespace, name


def group_icons_by_namespace(icons: set[str], default_namespace: str = 'ion') -> dict[str, set[str]]:
    """
    Group icon names by namespace.

    Args:
        icons: Set of icon names
        default_namespace: Default namespace for unqualified names

    Returns:
        Dictionary mapping namespace to set of icon names
    """
    grouped: dict[str, set[str]] = {}

    for icon in icons:
        namespace, name = parse_icon_name(icon, default_namespace)
        if namespace not in grouped:
            grouped[namespace] = set()
        grouped[namespace].add(name)

    return grouped
