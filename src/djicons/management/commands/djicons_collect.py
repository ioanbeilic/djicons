"""
Django management command to collect used icons.

Scans all templates for icon usages and downloads only the
icons that are actually used.

Supports two modes:
- Per-app (default): saves icons into each app's static/icons/ directory
- Central: saves all icons to a single output directory

Usage:
    python manage.py djicons_collect              # per-app (default)
    python manage.py djicons_collect --central    # central directory
    python manage.py djicons_collect --dry-run
"""

import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand

from djicons.conf import get_setting
from djicons.loaders.cdn import CDN_TEMPLATES
from djicons.scanner import (
    group_icons_by_namespace,
    scan_templates,
    scan_templates_per_app,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Collect used icons from templates and download them locally"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            help='Output directory for central mode (default: DJICONS["COLLECT_DIR"])',
        )
        parser.add_argument(
            "--central",
            action="store_true",
            help="Save all icons to a single central directory instead of per-app",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be downloaded without actually downloading",
        )
        parser.add_argument(
            "--timeout",
            type=float,
            default=10.0,
            help="HTTP timeout for downloading icons (default: 10 seconds)",
        )

    def handle(self, *args, **options):
        if options["central"]:
            self._handle_central(options)
        else:
            self._handle_per_app(options)

    def _download_icon(self, name, namespace, dest_path, timeout, verbose):
        """Download a single icon from CDN. Returns True on success."""
        cdn_url = CDN_TEMPLATES.get(namespace)
        if not cdn_url:
            return None  # no CDN for this namespace

        if dest_path.exists():
            if verbose:
                self.stdout.write(f"    [EXISTS] {name}")
            return True

        url = cdn_url.format(name=name)
        try:
            with urlopen(url, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                dest_path.write_text(content)
                if verbose:
                    self.stdout.write(self.style.SUCCESS(f"    [OK] {name}"))
                return True
        except HTTPError as e:
            if e.code == 404:
                self.stdout.write(self.style.ERROR(f"    [NOT FOUND] {name}"))
            else:
                self.stdout.write(self.style.ERROR(f"    [HTTP {e.code}] {name}"))
        except URLError as e:
            self.stdout.write(self.style.ERROR(f"    [NETWORK ERROR] {name}: {e.reason}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    [ERROR] {name}: {e}"))
        return False

    def _handle_per_app(self, options):
        """Collect icons into each app's static/icons/ directory."""
        dry_run = options["dry_run"]
        verbose = options["verbosity"] >= 2
        timeout = options["timeout"]
        default_namespace = get_setting("DEFAULT_NAMESPACE") or "ion"

        self.stdout.write(self.style.MIGRATE_HEADING(
            "Scanning templates for icon usages (per-app mode)..."
        ))

        per_app = scan_templates_per_app(default_namespace)

        if not per_app:
            self.stdout.write(self.style.WARNING("No icons found in templates."))
            return

        # Count total unique icons
        all_icons = set()
        for grouped in per_app.values():
            for names in grouped.values():
                all_icons.update(names)
        self.stdout.write(f"Found icons across {len(per_app)} apps.")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no icons downloaded.\n"))
            for app_path, grouped in sorted(per_app.items()):
                static_dir = app_path / "static" / "icons"
                self.stdout.write(f"\n{app_path.name}/ → {static_dir}")
                for namespace, names in sorted(grouped.items()):
                    self.stdout.write(f"  {namespace}: {', '.join(sorted(names))}")
            return

        total_downloaded = 0
        total_failed = 0
        total_skipped_ns = 0

        for app_path, grouped in sorted(per_app.items()):
            self.stdout.write(f"\n{self.style.MIGRATE_HEADING(app_path.name)}")

            for namespace, names in sorted(grouped.items()):
                cdn_url = CDN_TEMPLATES.get(namespace)
                if not cdn_url:
                    if verbose:
                        self.stdout.write(
                            self.style.WARNING(f'  No CDN for "{namespace}", skipping...')
                        )
                    total_skipped_ns += 1
                    continue

                # Create static/icons/{namespace}/ inside this app
                icons_dir = app_path / "static" / "icons" / namespace
                icons_dir.mkdir(parents=True, exist_ok=True)

                self.stdout.write(f"  {namespace}: {len(names)} icons → {icons_dir}")

                for name in sorted(names):
                    svg_path = icons_dir / f"{name}.svg"
                    result = self._download_icon(name, namespace, svg_path, timeout, verbose)
                    if result is True:
                        total_downloaded += 1
                    elif result is False:
                        total_failed += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Downloaded: {total_downloaded} icons across {len(per_app)} apps"))
        if total_failed:
            self.stdout.write(self.style.ERROR(f"Failed: {total_failed} icons"))

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Next steps:"))
        self.stdout.write("""
For production, configure djicons to load from local app directories:

DJICONS = {
    "MODE": "local",
}

Each app now has its icons in its own static/icons/ directory,
which Django's staticfiles finders will discover automatically.
""")

    def _handle_central(self, options):
        """Collect all icons to a single central directory (legacy mode)."""
        dry_run = options["dry_run"]
        verbose = options["verbosity"] >= 2
        timeout = options["timeout"]

        output_dir = options["output"]
        if not output_dir:
            output_dir = get_setting("COLLECT_DIR")
        if not output_dir:
            output_dir = Path(settings.BASE_DIR) / "static" / "icons"

        output_path = Path(output_dir)

        self.stdout.write(self.style.MIGRATE_HEADING("Scanning templates for icon usages..."))

        icons = scan_templates()

        if not icons:
            self.stdout.write(self.style.WARNING("No icons found in templates."))
            return

        self.stdout.write(f"Found {len(icons)} unique icons in templates.")

        default_namespace = get_setting("DEFAULT_NAMESPACE") or "ion"
        grouped = group_icons_by_namespace(icons, default_namespace)

        if verbose:
            for namespace, names in sorted(grouped.items()):
                self.stdout.write(f"  {namespace}: {len(names)} icons")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no icons downloaded."))
            self.stdout.write("\nIcons that would be downloaded:")
            for namespace, names in sorted(grouped.items()):
                self.stdout.write(f"\n{namespace}:")
                for name in sorted(names):
                    self.stdout.write(f"  - {name}")
            return

        output_path.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.MIGRATE_HEADING("\nDownloading icons..."))

        total_downloaded = 0
        total_failed = 0

        for namespace, names in grouped.items():
            namespace_dir = output_path / namespace
            namespace_dir.mkdir(exist_ok=True)

            cdn_url = CDN_TEMPLATES.get(namespace)
            if not cdn_url:
                self.stdout.write(
                    self.style.WARNING(f'  No CDN URL for namespace "{namespace}", skipping...')
                )
                continue

            self.stdout.write(f"\n{namespace}: {len(names)} icons")

            for name in sorted(names):
                svg_path = namespace_dir / f"{name}.svg"
                result = self._download_icon(name, namespace, svg_path, timeout, verbose)
                if result is True:
                    total_downloaded += 1
                elif result is False:
                    total_failed += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Downloaded: {total_downloaded} icons"))
        if total_failed:
            self.stdout.write(self.style.ERROR(f"Failed: {total_failed} icons"))
        self.stdout.write(f"Output: {output_path}")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Next steps:"))
        self.stdout.write(f'''
Add to your settings.py for production:

DJICONS = {{
    "MODE": "local",
    "COLLECT_DIR": "{output_path}",
}}
''')
