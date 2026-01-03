#!/usr/bin/env python3
"""
Download icon packs for djicons.

This script downloads SVG icons from various icon libraries and
saves them to the appropriate pack directories.

Usage:
    python scripts/download_icons.py              # Download all packs
    python scripts/download_icons.py ionicons     # Download specific pack
    python scripts/download_icons.py --list       # List available packs

Requirements:
    pip install httpx  # For async HTTP requests
"""

import argparse
import asyncio
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    raise SystemExit(1)

# Base directory for packs
PACKS_DIR = Path(__file__).parent.parent / "src" / "djicons" / "packs"

# Icon pack configurations
PACKS = {
    "ionicons": {
        "name": "Ionicons",
        "version": "7.4.0",
        "url": "https://github.com/ionic-team/ionicons/archive/refs/tags/v7.4.0.zip",
        "svg_path": "ionicons-7.4.0/src/svg",
        "transform": None,
    },
    "heroicons": {
        "name": "Heroicons",
        "version": "2.2.0",
        "url": "https://github.com/tailwindlabs/heroicons/archive/refs/tags/v2.2.0.zip",
        "svg_paths": [
            ("heroicons-2.2.0/optimized/24/outline", "outline"),
            ("heroicons-2.2.0/optimized/24/solid", "solid"),
            ("heroicons-2.2.0/optimized/20/solid", "mini"),
        ],
        "transform": "heroicons",
    },
    "material": {
        "name": "Material Symbols",
        "version": "latest",
        "url": "https://github.com/AviDuda/google-material-icons/archive/refs/heads/main.zip",
        "svg_path": "google-material-icons-main/icons/svg/outlined",
        "transform": "material",
    },
    "tabler": {
        "name": "Tabler Icons",
        "version": "3.28.1",
        "url": "https://github.com/tabler/tabler-icons/archive/refs/tags/v3.28.1.zip",
        "svg_paths": [
            ("tabler-icons-3.28.1/icons/outline", "outline"),
            ("tabler-icons-3.28.1/icons/filled", "filled"),
        ],
        "transform": "tabler",
    },
    "lucide": {
        "name": "Lucide Icons",
        "version": "0.469.0",
        "url": "https://github.com/lucide-icons/lucide/archive/refs/tags/0.469.0.zip",
        "svg_path": "lucide-0.469.0/icons",
        "transform": None,
    },
    "fontawesome": {
        "name": "Font Awesome Free",
        "version": "6.7.2",
        "url": "https://github.com/FortAwesome/Font-Awesome/archive/refs/tags/6.7.2.zip",
        "svg_paths": [
            ("Font-Awesome-6.7.2/svgs/solid", "solid"),
            ("Font-Awesome-6.7.2/svgs/regular", "regular"),
            ("Font-Awesome-6.7.2/svgs/brands", "brands"),
        ],
        "transform": "fontawesome",
    },
}


def transform_heroicons(name: str, style: str) -> str:
    """Transform Heroicons filename to include style suffix."""
    if style == "outline":
        return name
    return f"{name}-{style}"


def transform_material(name: str, style: str = "") -> str:
    """Transform Material Icons filename (underscores to dashes)."""
    return name.replace("_", "-")


def transform_tabler(name: str, style: str) -> str:
    """Transform Tabler Icons filename to include style suffix."""
    if style == "outline":
        return name
    return f"{name}-{style}"


def transform_fontawesome(name: str, style: str) -> str:
    """Transform Font Awesome filename to include style suffix."""
    # solid is default, others get suffix
    if style == "solid":
        return name
    return f"{name}-{style}"


TRANSFORMS = {
    "heroicons": transform_heroicons,
    "material": transform_material,
    "tabler": transform_tabler,
    "fontawesome": transform_fontawesome,
}


async def download_file(client: httpx.AsyncClient, url: str, dest: Path) -> None:
    """Download a file from URL to destination."""
    print(f"  Downloading from {url}...")
    response = await client.get(url, follow_redirects=True)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"  Downloaded {len(response.content) / 1024 / 1024:.1f} MB")


def extract_svgs(
    zip_path: Path,
    pack_name: str,
    config: dict,
    output_dir: Path,
) -> int:
    """Extract SVG files from zip to output directory."""
    count = 0
    transform_fn = TRANSFORMS.get(config.get("transform"))

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Handle multiple paths (like heroicons with outline/solid/mini)
        if "svg_paths" in config:
            for svg_path, style in config["svg_paths"]:
                for name in zf.namelist():
                    if name.startswith(svg_path) and name.endswith(".svg"):
                        # Read SVG content
                        svg_content = zf.read(name).decode("utf-8")

                        # Get filename
                        filename = Path(name).stem
                        if transform_fn:
                            filename = transform_fn(filename, style)

                        # Write to output
                        output_file = output_dir / f"{filename}.svg"
                        output_file.write_text(svg_content)
                        count += 1
        else:
            # Single path
            svg_path = config["svg_path"]
            for name in zf.namelist():
                if name.startswith(svg_path) and name.endswith(".svg"):
                    # Read SVG content
                    svg_content = zf.read(name).decode("utf-8")

                    # Get filename
                    filename = Path(name).stem
                    if transform_fn:
                        filename = transform_fn(filename, "")

                    # Write to output
                    output_file = output_dir / f"{filename}.svg"
                    output_file.write_text(svg_content)
                    count += 1

    return count


async def download_pack(pack_name: str) -> None:
    """Download and install an icon pack."""
    if pack_name not in PACKS:
        print(f"Unknown pack: {pack_name}")
        print(f"Available packs: {', '.join(PACKS.keys())}")
        return

    config = PACKS[pack_name]
    print(f"\n{'=' * 60}")
    print(f"Downloading {config['name']} v{config['version']}")
    print(f"{'=' * 60}")

    # Create output directory
    output_dir = PACKS_DIR / pack_name / "icons"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing icons
    for svg_file in output_dir.glob("*.svg"):
        svg_file.unlink()

    # Download zip
    async with httpx.AsyncClient(timeout=60.0) as client:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            await download_file(client, config["url"], tmp_path)

            # Extract SVGs
            print("  Extracting SVGs...")
            count = extract_svgs(tmp_path, pack_name, config, output_dir)
            print(f"  Extracted {count} icons to {output_dir}")

        finally:
            tmp_path.unlink(missing_ok=True)


async def download_all() -> None:
    """Download all icon packs."""
    for pack_name in PACKS:
        await download_pack(pack_name)


def list_packs() -> None:
    """List available icon packs and their status."""
    print("\nAvailable icon packs:")
    print("-" * 60)

    for pack_name, config in PACKS.items():
        icons_dir = PACKS_DIR / pack_name / "icons"
        icon_count = len(list(icons_dir.glob("*.svg"))) if icons_dir.exists() else 0
        status = f"{icon_count} icons" if icon_count > 0 else "not installed"

        print(f"  {pack_name:12} {config['name']:20} v{config['version']:10} ({status})")

    print()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download icon packs for djicons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_icons.py              Download all icon packs
  python download_icons.py ionicons     Download only Ionicons
  python download_icons.py heroicons tabler   Download multiple packs
  python download_icons.py --list       List available packs
        """,
    )
    parser.add_argument(
        "packs",
        nargs="*",
        help="Icon packs to download (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available icon packs",
    )

    args = parser.parse_args()

    if args.list:
        list_packs()
        return

    if args.packs:
        for pack_name in args.packs:
            asyncio.run(download_pack(pack_name))
    else:
        asyncio.run(download_all())

    print("\nDone! Icon packs have been installed.")
    print("You can now use them in your Django templates:")
    print('  {% load djicons %}')
    print('  {% icon "ion:home" %}')


if __name__ == "__main__":
    main()
