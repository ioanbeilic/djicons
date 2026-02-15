"""
Django management command to collect used icons.

Scans all templates for icon usages and downloads only the
icons that are actually used, saving them to COLLECT_DIR.

Usage:
    python manage.py djicons_collect
    python manage.py djicons_collect --output ./static/icons
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
from djicons.scanner import group_icons_by_namespace, scan_templates

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Collect used icons from templates and download them locally"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            help='Output directory for collected icons (default: DJICONS["COLLECT_DIR"])',
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
        # Note: Django's BaseCommand already provides --verbosity/-v,
        # so we use that instead of a custom --verbose flag.

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbosity"] >= 2
        timeout = options["timeout"]

        # Determine output directory
        output_dir = options["output"]
        if not output_dir:
            output_dir = get_setting("COLLECT_DIR")
        if not output_dir:
            output_dir = Path(settings.BASE_DIR) / "static" / "icons"

        output_path = Path(output_dir)

        self.stdout.write(self.style.MIGRATE_HEADING("Scanning templates for icon usages..."))

        # Scan templates
        icons = scan_templates()

        if not icons:
            self.stdout.write(self.style.WARNING("No icons found in templates."))
            return

        self.stdout.write(f"Found {len(icons)} unique icons in templates.")

        # Group by namespace
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

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Download icons
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

                # Skip if already exists
                if svg_path.exists():
                    if verbose:
                        self.stdout.write(f"  [EXISTS] {name}")
                    total_downloaded += 1
                    continue

                # Download from CDN
                url = cdn_url.format(name=name)
                try:
                    with urlopen(url, timeout=timeout) as response:
                        content = response.read().decode("utf-8")
                        svg_path.write_text(content)
                        total_downloaded += 1
                        if verbose:
                            self.stdout.write(self.style.SUCCESS(f"  [OK] {name}"))
                except HTTPError as e:
                    total_failed += 1
                    if e.code == 404:
                        self.stdout.write(self.style.ERROR(f"  [NOT FOUND] {name}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"  [HTTP {e.code}] {name}"))
                except URLError as e:
                    total_failed += 1
                    self.stdout.write(self.style.ERROR(f"  [NETWORK ERROR] {name}: {e.reason}"))
                except Exception as e:
                    total_failed += 1
                    self.stdout.write(self.style.ERROR(f"  [ERROR] {name}: {e}"))

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Downloaded: {total_downloaded} icons"))
        if total_failed:
            self.stdout.write(self.style.ERROR(f"Failed: {total_failed} icons"))
        self.stdout.write(f"Output: {output_path}")

        # Hint about configuration
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Next steps:"))
        self.stdout.write(f'''
Add to your settings.py for production:

DJICONS = {{
    "MODE": "local",
    "COLLECT_DIR": "{output_path}",
}}
''')
