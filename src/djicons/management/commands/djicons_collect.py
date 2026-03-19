"""
Django management command to collect used icons.

Scans all templates for icon usages and downloads only the
icons that are actually used.

Supports three modes:
- Per-app (default): saves icons into each app's static/icons/ directory
- Central: saves all icons to a single output directory
- S3: downloads icons from CDN and uploads them to S3

Usage:
    python manage.py djicons_collect              # per-app (default)
    python manage.py djicons_collect --central    # central directory
    python manage.py djicons_collect --s3         # upload to S3
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
    help = "Collect used icons from templates and download them locally or to S3"

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
            "--s3",
            action="store_true",
            help="Upload icons to S3 (uses DJICONS['S3'] config)",
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
        if options["s3"]:
            self._handle_s3(options)
        elif options["central"]:
            self._handle_central(options)
        else:
            self._handle_per_app(options)

    def _download_icon_content(self, name, namespace, timeout):
        """Download icon SVG content from CDN. Returns (content, error_msg)."""
        cdn_url = CDN_TEMPLATES.get(namespace)
        if not cdn_url:
            return None, None  # no CDN for this namespace

        url = cdn_url.format(name=name)
        try:
            with urlopen(url, timeout=timeout) as response:
                return response.read().decode("utf-8"), None
        except HTTPError as e:
            if e.code == 404:
                return None, f"[NOT FOUND] {name}"
            return None, f"[HTTP {e.code}] {name}"
        except URLError as e:
            return None, f"[NETWORK ERROR] {name}: {e.reason}"
        except Exception as e:
            return None, f"[ERROR] {name}: {e}"

    def _download_icon(self, name, namespace, dest_path, timeout, verbose):
        """Download a single icon from CDN to disk. Returns True on success."""
        cdn_url = CDN_TEMPLATES.get(namespace)
        if not cdn_url:
            return None  # no CDN for this namespace

        if dest_path.exists():
            if verbose:
                self.stdout.write(f"    [EXISTS] {name}")
            return True

        content, error = self._download_icon_content(name, namespace, timeout)
        if content:
            dest_path.write_text(content)
            if verbose:
                self.stdout.write(self.style.SUCCESS(f"    [OK] {name}"))
            return True
        if error:
            self.stdout.write(self.style.ERROR(f"    {error}"))
        return False

    def _handle_s3(self, options):
        """Collect icons and upload them to S3."""
        dry_run = options["dry_run"]
        verbose = options["verbosity"] >= 2
        timeout = options["timeout"]

        s3_config = get_setting("S3")
        if not s3_config:
            self.stderr.write(
                self.style.ERROR(
                    'S3 not configured. Add DJICONS["S3"] to your settings:\n\n'
                    "DJICONS = {\n"
                    '    "S3": {\n'
                    '        "bucket": "my-bucket",\n'
                    '        "region": "eu-west-1",\n'
                    '        "prefix": "djicons/icons/",\n'
                    "    }\n"
                    "}\n"
                )
            )
            return

        bucket = s3_config.get("bucket")
        region = s3_config.get("region", "us-east-1")
        prefix = s3_config.get("prefix", "djicons/icons/")
        aws_key = s3_config.get("aws_access_key_id")
        aws_secret = s3_config.get("aws_secret_access_key")

        if not bucket:
            self.stderr.write(self.style.ERROR('S3 "bucket" is required.'))
            return

        # Ensure prefix ends with /
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        self.stdout.write(self.style.MIGRATE_HEADING("Scanning templates for icon usages..."))

        icons = scan_templates()

        if not icons:
            self.stdout.write(self.style.WARNING("No icons found in templates."))
            return

        default_namespace = get_setting("DEFAULT_NAMESPACE") or "ion"
        grouped = group_icons_by_namespace(icons, default_namespace)

        self.stdout.write(f"Found {len(icons)} unique icons in templates.")
        self.stdout.write(f"Target: s3://{bucket}/{prefix}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no icons uploaded."))
            self.stdout.write("\nIcons that would be uploaded:")
            for namespace, names in sorted(grouped.items()):
                self.stdout.write(f"\n{namespace}:")
                for name in sorted(names):
                    self.stdout.write(f"  - {name} → {prefix}{namespace}/{name}.svg")
            return

        # Initialize S3 loader for uploads
        from djicons.loaders.s3 import S3IconLoader

        total_uploaded = 0
        total_existed = 0
        total_failed = 0

        for namespace, names in sorted(grouped.items()):
            cdn_url = CDN_TEMPLATES.get(namespace)
            if not cdn_url:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(f'  No CDN for "{namespace}", skipping...')
                    )
                continue

            ns_prefix = f"{prefix}{namespace}"
            loader = S3IconLoader(
                bucket=bucket,
                prefix=ns_prefix,
                region=region,
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
            )

            if loader.client is None:
                self.stderr.write(
                    self.style.ERROR("boto3 is not installed. Run: pip install boto3")
                )
                return

            # Check which icons already exist in S3
            existing = set(loader.list())

            self.stdout.write(f"\n{namespace}: {len(names)} icons → s3://{bucket}/{ns_prefix}/")

            for name in sorted(names):
                if name in existing:
                    if verbose:
                        self.stdout.write(f"    [EXISTS] {name}")
                    total_existed += 1
                    continue

                content, error = self._download_icon_content(name, namespace, timeout)
                if content:
                    if loader.upload(name, content):
                        if verbose:
                            self.stdout.write(self.style.SUCCESS(f"    [OK] {name}"))
                        total_uploaded += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"    [S3 UPLOAD FAILED] {name}"))
                        total_failed += 1
                elif error:
                    self.stdout.write(self.style.ERROR(f"    {error}"))
                    total_failed += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Uploaded: {total_uploaded} icons | "
                f"Already existed: {total_existed} | "
                f"Failed: {total_failed}"
            )
        )

        # Build namespaces config for the user
        namespaces_config = {}
        for namespace in sorted(grouped.keys()):
            if CDN_TEMPLATES.get(namespace):
                namespaces_config[namespace] = f"{prefix}{namespace}/"

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Next steps:"))

        ns_lines = "\n".join(f'            "{ns}": "{p}",' for ns, p in namespaces_config.items())
        self.stdout.write(
            f"""
Configure djicons to load from S3:

DJICONS = {{
    "MODE": "s3",
    "S3": {{
        "bucket": "{bucket}",
        "region": "{region}",
        "prefix": "{prefix}",
        "namespaces": {{
{ns_lines}
        }},
    }},
}}
"""
        )

    def _handle_per_app(self, options):
        """Collect icons into each app's static/icons/ directory."""
        dry_run = options["dry_run"]
        verbose = options["verbosity"] >= 2
        timeout = options["timeout"]
        default_namespace = get_setting("DEFAULT_NAMESPACE") or "ion"

        self.stdout.write(
            self.style.MIGRATE_HEADING("Scanning templates for icon usages (per-app mode)...")
        )

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
        self.stdout.write(
            self.style.SUCCESS(f"Downloaded: {total_downloaded} icons across {len(per_app)} apps")
        )
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
