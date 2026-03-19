# djicons

Multi-library SVG icon system for Django. Like [react-icons](https://react-icons.github.io/react-icons/), but 100% backend-driven.

**Zero-config development. Minimal production builds.**

## Features

- **Multi-library support**: Ionicons, Heroicons, Material Symbols, Tabler, Lucide, Font Awesome
- **CDN mode for development**: Access all ~177,000 icons without downloading anything
- **Smart collection for production**: Only download the icons you actually use
- **SVG inline rendering**: Full CSS control, no font loading
- **Namespace system**: `{% icon "ion:home" %}`, `{% icon "hero:pencil" %}`
- **S3 loader**: Load icons from AWS S3 for shared icon libraries across projects
- **LRU caching**: Fast rendering with memory + optional Django cache
- **Django 4.2 – 6.0**: Fully compatible with modern Django

## Installation

```bash
pip install djicons
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'djicons',
    # ...
]
```

**That's it!** Start using icons immediately - no download required in development.

## How It Works

### Development (default)
Icons are fetched from CDN on demand. Zero setup, access to all ~177,000 icons.

### Production (local)
Run `djicons_collect` to download only the icons used in your templates:

```bash
python manage.py djicons_collect
```

This scans your templates, finds all `{% icon %}` usages, and downloads only those icons (~KBs instead of ~700MB).

### Production (S3 — shared across projects)
Collect icons and upload them to S3, then all your projects load icons from the same bucket:

```bash
python manage.py djicons_collect --s3
```

## Quick Start

```django
{% load djicons %}

{# Basic usage #}
{% icon "home" %}

{# With namespace (explicit library) #}
{% icon "ion:cart-outline" %}
{% icon "hero:pencil-square" %}
{% icon "material:shopping_cart" %}
{% icon "tabler:home" %}
{% icon "lucide:settings" %}
{% icon "fa:house" %}
{% icon "fa:github-brands" %}

{# With size #}
{% icon "ion:home" size=24 %}

{# With CSS classes #}
{% icon "hero:pencil" css_class="w-5 h-5 text-blue-500" %}

{# With color #}
{% icon "ion:heart" color="#ff0000" %}
{% icon "ion:heart" fill="currentColor" %}

{# With ARIA accessibility #}
{% icon "ion:menu" aria_label="Open menu" %}

{# With data attributes #}
{% icon "ion:close" data_action="dismiss" data_target="#modal" %}

{# Store in variable #}
{% icon "ion:home" as home_icon %}
{{ home_icon }}
```

## Available Icon Packs

| Pack | Namespace | Icons | License |
|------|-----------|-------|---------|
| [Ionicons](https://ionicons.com) | `ion:` | ~1,400 | MIT |
| [Heroicons](https://heroicons.com) | `hero:` | ~300 | MIT |
| [Material Symbols](https://fonts.google.com/icons) | `material:` | ~2,500 | Apache 2.0 |
| [Tabler Icons](https://tabler.io/icons) | `tabler:` | ~5,000 | MIT |
| [Lucide](https://lucide.dev) | `lucide:` | ~1,500 | ISC |
| [Font Awesome Free](https://fontawesome.com) | `fa:` | ~2,000 | CC BY 4.0 / MIT |

**Total: ~12,700 icons**

### Font Awesome Styles

Font Awesome icons come in three styles:

```django
{% icon "fa:house" %}              {# solid (default) #}
{% icon "fa:heart-regular" %}      {# regular/outlined #}
{% icon "fa:github-brands" %}      {# brand logos #}
```

**Note:** Font Awesome Free requires attribution. See [fontawesome.com/license](https://fontawesome.com/license/free)

## Configuration

### Development (CDN mode - default)

```python
# settings.py - Development
DJICONS = {
    'MODE': 'cdn',  # Fetch from CDN (default)
}
```

### Production (Local mode)

```python
# settings.py - Production
DJICONS = {
    'MODE': 'local',
    'COLLECT_DIR': BASE_DIR / 'static' / 'icons',  # Where collected icons are stored
}
```

### Production (S3 mode — shared across projects)

```python
# settings.py - Production (S3)
DJICONS = {
    'MODE': 's3',
    'S3': {
        'bucket': 'my-bucket',
        'region': 'eu-west-1',
        'prefix': 'djicons/icons/',
        'namespaces': {
            'ion': 'djicons/icons/ion/',
            'hero': 'djicons/icons/hero/',
            'material': 'djicons/icons/material/',
        },
    },
}
```

All projects sharing the same S3 bucket will use the same icons. You can also upload custom SVGs directly to S3 under the appropriate prefix.

### Full Configuration Options

```python
DJICONS = {
    # Mode: 'cdn' (development), 'local' (production), or 's3' (shared)
    'MODE': 'cdn',

    # Default namespace for unqualified names
    'DEFAULT_NAMESPACE': 'ion',

    # Directory for collected icons (production)
    'COLLECT_DIR': BASE_DIR / 'static' / 'icons',

    # Icon packs to enable
    'PACKS': ['ionicons', 'heroicons', 'material', 'tabler', 'lucide', 'fontawesome'],

    # Custom icon directories by namespace
    'ICON_DIRS': {
        'custom': BASE_DIR / 'static' / 'my-icons',
    },

    # Return empty string for missing icons (vs raising error)
    'MISSING_ICON_SILENT': True,

    # Default CSS class for all icons
    'DEFAULT_CLASS': '',

    # Default icon size
    'DEFAULT_SIZE': None,

    # Add aria-hidden by default
    'ARIA_HIDDEN': True,

    # Semantic aliases
    'ALIASES': {
        'edit': 'hero:pencil',
        'delete': 'hero:trash',
        'add': 'ion:add-outline',
    },
}
```

## Collecting Icons for Production

The `djicons_collect` command scans your templates and downloads only the icons you use:

```bash
# Per-app mode (default): saves icons into each app's static/icons/ directory
python manage.py djicons_collect

# Central mode: saves all icons to a single directory
python manage.py djicons_collect --central

# Specify custom output directory (central mode)
python manage.py djicons_collect --central --output ./static/icons

# S3 mode: download from CDN and upload to S3
python manage.py djicons_collect --s3

# S3 mode: also upload icons from a local directory
python manage.py djicons_collect --s3 --upload-dir ion:/path/to/ionicons/svg

# Preview what would be downloaded (dry run)
python manage.py djicons_collect --dry-run

# Verbose output
python manage.py djicons_collect -v2
```

### Per-app mode (default)

Ideal for modular projects — each app owns its icons and Django's staticfiles finders discover them automatically.

When you run `djicons_collect` (without flags), it scans each app's templates, finds all `{% icon %}` usages, and downloads the SVGs into the app's own `static/icons/` directory:

```
myapp/
├── templates/myapp/
│   └── index.html          # {% icon "ion:home" %} {% icon "hero:pencil" %}
└── static/
    └── icons/
        ├── ion/
        │   └── home.svg     # downloaded automatically
        └── hero/
            └── pencil.svg   # downloaded automatically
```

This is the recommended workflow for **module/app developers**:

1. **During development**: use `MODE: 'cdn'` — icons load from CDN, nothing saved to disk
2. **Before publishing**: run `python manage.py djicons_collect` — downloads only the icons your module uses
3. **In production**: `_register_app_icons()` discovers each app's `static/icons/` automatically — no CDN needed

The module ships with its own icons, making it self-contained and offline-ready.

### S3 mode

For shared icon storage across multiple projects. Add `djicons_collect --s3` to your Docker entrypoint or deploy script — it runs alongside `collectstatic`:

```dockerfile
# In your entrypoint or CMD
python manage.py migrate --noinput
python manage.py djicons_collect --s3
exec gunicorn ...
```

The command is **idempotent** — icons already in S3 are skipped. It also uploads any local directories configured in `ICON_DIRS`.

The `--upload-dir` flag lets you upload additional local icon directories:

```bash
# Upload ionicons from a local path
python manage.py djicons_collect --s3 --upload-dir ion:/path/to/ionicons/svg

# Upload multiple directories
python manage.py djicons_collect --s3 \
    --upload-dir ion:/path/to/ionicons \
    --upload-dir hero:/path/to/heroicons
```

### Custom Icon Directories

Use `ICON_DIRS` to load icons from your project's static directory:

```python
from pathlib import Path

DJICONS = {
    'ICON_DIRS': {
        # Load ionicons from your static folder
        'ion': BASE_DIR / 'static' / 'ionicons' / 'dist' / 'svg',
        # Add your own custom icons
        'app': BASE_DIR / 'static' / 'icons',
    },
    # Disable bundled packs if you don't need them
    'PACKS': [],
}
```

Icons in `ICON_DIRS` take priority over bundled packs, so you can override specific icons.

### S3 Icon Loader

Share icons across multiple Django projects via a single S3 bucket. Three steps:

**1. Collect and upload icons to S3:**
```bash
python manage.py djicons_collect --s3
```

**2. Configure all projects to load from S3:**
```python
DJICONS = {
    'MODE': 's3',
    'S3': {
        'bucket': 'my-bucket',
        'region': 'eu-west-1',
        'prefix': 'djicons/icons/',
        'namespaces': {
            'ion': 'djicons/icons/ion/',
            'hero': 'djicons/icons/hero/',
        },
    },
}
```

**3. (Optional) Upload custom SVGs directly to S3:**

You can also manually upload SVG files to `s3://my-bucket/djicons/icons/{namespace}/{name}.svg` and they will be available in all projects.

Credentials are resolved via boto3's standard chain (IAM role, env vars, `~/.aws/credentials`). Requires `boto3`:

```bash
pip install boto3
```

If boto3 is not installed, the S3 loader silently does nothing and falls back to other loaders.

You can also use the loader programmatically:

```python
from djicons.loaders import S3IconLoader

loader = S3IconLoader(bucket="my-bucket", prefix="djicons/icons/custom/", region="eu-west-1")
icons.register_loader(loader, namespace="custom")
```

## Programmatic Usage

```python
from djicons import icons, Icon, get, register
from djicons.loaders import DirectoryIconLoader, S3IconLoader

# Get an icon
icon = icons.get("ion:home")
html = icon.render(size=24, css_class="text-primary")

# Shortcut function
html = get("ion:home", size=24)

# Register custom icon
icons.register("my-icon", "<svg>...</svg>", namespace="myapp")

# Register a directory of icons
loader = DirectoryIconLoader("/path/to/icons")
icons.register_loader(loader, namespace="custom")

# Create aliases
icons.register_alias("edit", "hero:pencil")

# List icons
all_icons = icons.list_icons()
ion_icons = icons.list_icons("ion")
namespaces = icons.list_namespaces()
```

## Icon Class API

```python
from djicons import Icon

icon = Icon(
    name="home",
    svg_content="<svg>...</svg>",
    namespace="myapp",
    category="navigation",
    tags=["house", "main"],
)

# Render with options
html = icon.render(
    size=24,              # width & height
    width=24,             # or separate
    height=24,
    css_class="icon",     # CSS classes
    color="#000",         # CSS color
    fill="currentColor",  # SVG fill
    stroke="#000",        # SVG stroke
    aria_label="Home",    # Accessibility
    aria_hidden=True,     # Hide from screen readers
    data_action="click",  # data-* attributes
)
```

## ERPlora Integration

For [ERPlora](https://github.com/ERPlora/erplora) modules:

```python
# In your module's apps.py
from django.apps import AppConfig

class InventoryConfig(AppConfig):
    name = 'inventory'

    def ready(self):
        from djicons.contrib.erplora import register_module_icons
        register_module_icons(self.name, self.path)
```

Or auto-discover all modules:

```python
# In Django settings or ready()
from djicons.contrib.erplora import discover_module_icons

discover_module_icons("/path/to/modules")
```

Then use in templates:

```django
{% icon "inventory:box" %}
{% icon "sales:receipt" %}
```

## Template Tags Reference

### `{% icon %}`

Render an SVG icon inline.

```django
{% icon name [size=N] [width=N] [height=N] [css_class="..."] [color="..."] [fill="..."] [stroke="..."] [aria_label="..."] [aria_hidden=True|False] [**attrs] %}
```

### `{% icon_exists %}`

Check if an icon exists.

```django
{% icon_exists "ion:home" as has_home %}
{% if has_home %}...{% endif %}
```

### `{% icon_list %}`

List available icons.

```django
{% icon_list "ion" as ionicons %}
{% for name in ionicons %}
    {% icon name size=24 %}
{% endfor %}
```

### `{% icon_sprite %}`

Render SVG sprite sheet (for advanced use).

```django
{% icon_sprite "ion" %}
```

## Development

```bash
# Clone repository
git clone https://github.com/djicons/djicons.git
cd djicons

# Install dependencies
pip install -e ".[dev]"

# Download icon packs
python scripts/download_icons.py

# Run tests
pytest

# Run linting
ruff check .
ruff format .
```

## License

MIT License - see [LICENSE](LICENSE) for details.

Icon packs are distributed under their respective licenses:
- [Ionicons](https://ionicons.com): MIT License
- [Heroicons](https://heroicons.com): MIT License
- [Material Symbols](https://fonts.google.com/icons): [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- [Tabler Icons](https://tabler.io/icons): MIT License
- [Lucide](https://lucide.dev): ISC License
- [Font Awesome Free](https://fontawesome.com): CC BY 4.0 (icons) / MIT (code)

**Note:** This project includes Material Icons by Google, licensed under the Apache License, Version 2.0.

## Credits

- Inspired by [react-icons](https://react-icons.github.io/react-icons/)
- Built for [ERPlora](https://github.com/ERPlora/erplora) modular ERP system
- Created by [Ioan Beilic](https://github.com/ioanbeilic)
