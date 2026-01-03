# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-03

### Added
- Initial release
- `IconRegistry` singleton for managing icons
- `Icon` class with SVG rendering capabilities
- `{% icon %}` template tag for Django templates
- `DirectoryIconLoader` for loading icons from filesystem
- Built-in icon packs: Ionicons, Heroicons, Material, Tabler, Lucide
- LRU memory cache for rendered icons
- Namespace support (e.g., `ion:home`, `hero:pencil`)
- ERPlora module integration via `djicons.contrib.erplora`
- Full ARIA accessibility support
- Custom CSS classes and HTML attributes
