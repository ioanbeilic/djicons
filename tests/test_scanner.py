"""Tests for template scanner."""

import tempfile
from pathlib import Path

import pytest

from djicons.scanner import (
    scan_file,
    scan_directory,
    parse_icon_name,
    group_icons_by_namespace,
    ICON_PATTERN,
)


class TestIconPattern:
    """Tests for icon regex pattern."""

    def test_matches_double_quotes(self):
        """Test pattern matches double-quoted icon names."""
        content = '{% icon "home" %}'
        matches = ICON_PATTERN.findall(content)
        assert matches == ["home"]

    def test_matches_single_quotes(self):
        """Test pattern matches single-quoted icon names."""
        content = "{% icon 'home' %}"
        matches = ICON_PATTERN.findall(content)
        assert matches == ["home"]

    def test_matches_namespaced_icon(self):
        """Test pattern matches namespaced icons."""
        content = '{% icon "ion:home-outline" %}'
        matches = ICON_PATTERN.findall(content)
        assert matches == ["ion:home-outline"]

    def test_matches_with_extra_spaces(self):
        """Test pattern matches with extra whitespace."""
        content = '{%  icon   "home"  %}'
        matches = ICON_PATTERN.findall(content)
        assert matches == ["home"]

    def test_matches_multiple_icons(self):
        """Test pattern finds multiple icons in content."""
        content = '''
        {% icon "home" %}
        {% icon "cart-outline" %}
        {% icon "hero:pencil" %}
        '''
        matches = ICON_PATTERN.findall(content)
        assert set(matches) == {"home", "cart-outline", "hero:pencil"}


class TestScanFile:
    """Tests for scan_file function."""

    def test_scan_file_with_icons(self):
        """Test scanning a file with icon usages."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write('''
            <div>{% icon "home" %}</div>
            <span>{% icon "cart" %}</span>
            ''')
            f.flush()

            icons = scan_file(Path(f.name))
            assert icons == {"home", "cart"}

    def test_scan_file_empty(self):
        """Test scanning a file with no icons."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write('<div>No icons here</div>')
            f.flush()

            icons = scan_file(Path(f.name))
            assert icons == set()

    def test_scan_nonexistent_file(self):
        """Test scanning a nonexistent file returns empty set."""
        icons = scan_file(Path("/nonexistent/file.html"))
        assert icons == set()


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_directory(self):
        """Test scanning a directory of templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create some template files
            (tmppath / "page1.html").write_text('{% icon "home" %}')
            (tmppath / "page2.html").write_text('{% icon "cart" %}')
            (tmppath / "ignore.txt").write_text('{% icon "ignored" %}')

            # Scan only .html files
            icons = scan_directory(tmppath, extensions=('.html',))
            assert icons == {"home", "cart"}

    def test_scan_directory_recursive(self):
        """Test scanning subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            subdir = tmppath / "partials"
            subdir.mkdir()

            (tmppath / "base.html").write_text('{% icon "home" %}')
            (subdir / "header.html").write_text('{% icon "menu" %}')

            icons = scan_directory(tmppath)
            assert icons == {"home", "menu"}


class TestParseIconName:
    """Tests for parse_icon_name function."""

    def test_simple_name(self):
        """Test parsing simple icon name."""
        namespace, name = parse_icon_name("home")
        assert namespace == "ion"
        assert name == "home"

    def test_namespaced_name(self):
        """Test parsing namespaced icon name."""
        namespace, name = parse_icon_name("hero:pencil")
        assert namespace == "hero"
        assert name == "pencil"

    def test_custom_default_namespace(self):
        """Test custom default namespace."""
        namespace, name = parse_icon_name("home", default_namespace="tabler")
        assert namespace == "tabler"
        assert name == "home"


class TestGroupIconsByNamespace:
    """Tests for group_icons_by_namespace function."""

    def test_group_mixed_icons(self):
        """Test grouping icons with mixed namespaces."""
        icons = {"home", "cart", "hero:pencil", "fa:github"}
        grouped = group_icons_by_namespace(icons)

        assert grouped["ion"] == {"home", "cart"}
        assert grouped["hero"] == {"pencil"}
        assert grouped["fa"] == {"github"}

    def test_group_all_same_namespace(self):
        """Test grouping icons all in same namespace."""
        icons = {"hero:pencil", "hero:trash", "hero:plus"}
        grouped = group_icons_by_namespace(icons)

        assert "hero" in grouped
        assert grouped["hero"] == {"pencil", "trash", "plus"}
        assert "ion" not in grouped

    def test_empty_set(self):
        """Test grouping empty set."""
        grouped = group_icons_by_namespace(set())
        assert grouped == {}
