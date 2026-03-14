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
ICON_PATTERN = re.compile(r'{%\s*icon\s+["\']([^"\']+)["\']', re.MULTILINE)


def get_template_dirs() -> list[Path]:
    """
    Get all template directories from Django settings.

    Returns:
        List of template directory paths
    """
    template_dirs: list[Path] = []

    # Get from TEMPLATES setting
    templates_config = getattr(settings, "TEMPLATES", [])
    for config in templates_config:
        # DIRS from each template backend
        for dir_path in config.get("DIRS", []):
            path = Path(dir_path)
            if path.exists():
                template_dirs.append(path)

        # APP_DIRS: scan each installed app's templates folder
        if config.get("APP_DIRS", False):
            for app in settings.INSTALLED_APPS:
                try:
                    # Get app path
                    module = __import__(app, fromlist=[""])
                    app_path = Path(module.__file__).parent
                    templates_path = app_path / "templates"
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
        content = file_path.read_text(encoding="utf-8")
        matches = ICON_PATTERN.findall(content)
        icons.update(matches)
    except (OSError, UnicodeDecodeError):
        pass

    return icons


def scan_directory(directory: Path, extensions: tuple[str, ...] = (".html", ".txt")) -> set[str]:
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
        for file_path in directory.rglob(f"*{ext}"):
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


def get_app_paths() -> list[tuple[Path, Path]]:
    """
    Get all Django app paths paired with their template directories.

    Returns:
        List of (app_path, templates_path) tuples
    """
    app_entries: list[tuple[Path, Path]] = []
    seen_templates: set[Path] = set()

    templates_config = getattr(settings, "TEMPLATES", [])
    for config in templates_config:
        # DIRS entries — these are standalone template dirs (not app-bound)
        # We include them mapped to themselves so they're still scanned
        for dir_path in config.get("DIRS", []):
            path = Path(dir_path).resolve()
            if path.exists() and path not in seen_templates:
                seen_templates.add(path)
                # Try to find the app root: if this is an app's templates/ dir
                if path.name == "templates" and (path.parent / "__init__.py").exists():
                    app_entries.append((path.parent, path))
                else:
                    app_entries.append((path, path))

        # APP_DIRS: each installed app's templates folder
        if config.get("APP_DIRS", False):
            for app in settings.INSTALLED_APPS:
                try:
                    module = __import__(app, fromlist=[""])
                    app_path = Path(module.__file__).parent
                    templates_path = (app_path / "templates").resolve()
                    if templates_path.exists() and templates_path not in seen_templates:
                        seen_templates.add(templates_path)
                        app_entries.append((app_path, templates_path))
                except (ImportError, AttributeError):
                    pass

    return app_entries


def scan_templates_per_app(
    default_namespace: str = "ion",
) -> dict[Path, dict[str, set[str]]]:
    """
    Scan all Django templates and group icons per app.

    Returns a mapping of app_path → {namespace: {icon_names}}.
    Only apps that have a static/ directory (or can have one created)
    are included with their own entry. Template dirs that don't belong
    to an app are grouped under a special key.

    Args:
        default_namespace: Default namespace for unqualified icon names

    Returns:
        Dict mapping app_path to {namespace: set of icon names}
    """
    result: dict[Path, dict[str, set[str]]] = {}

    for app_path, templates_path in get_app_paths():
        icons = scan_directory(templates_path)
        if not icons:
            continue

        grouped = group_icons_by_namespace(icons, default_namespace)

        if app_path in result:
            # Merge with existing entry
            for ns, names in grouped.items():
                if ns in result[app_path]:
                    result[app_path][ns].update(names)
                else:
                    result[app_path][ns] = names
        else:
            result[app_path] = grouped

    return result


def parse_icon_name(name: str, default_namespace: str = "ion") -> tuple[str, str]:
    """
    Parse an icon name into namespace and name.

    Args:
        name: Icon name (e.g., 'home', 'ion:home', 'hero:pencil')
        default_namespace: Default namespace if not specified

    Returns:
        Tuple of (namespace, icon_name)
    """
    if ":" in name:
        namespace, icon_name = name.split(":", 1)
        return namespace, icon_name
    return default_namespace, name


def group_icons_by_namespace(
    icons: set[str], default_namespace: str = "ion"
) -> dict[str, set[str]]:
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
