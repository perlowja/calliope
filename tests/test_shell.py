# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.templates.shell import (
    NavLink,
    base_path,
    html_footer,
    html_head,
    html_header,
    legal_block,
    navigation,
    section_grid,
    stat_grid,
)


def test_base_path_root():
    assert base_path(0) == "."


def test_base_path_one_deep():
    assert base_path(1) == "../"


def test_base_path_three_deep():
    assert base_path(3) == "../../../"


def test_base_path_rejects_negative():
    with pytest.raises(ValueError):
        base_path(-1)


def test_html_head_contains_essentials():
    out = html_head(
        title="Demo Page",
        site_name="Acme",
        description="A demo",
        stylesheets=("/main.css",),
        scripts=("/main.js",),
    )
    assert "<!DOCTYPE html>" in out
    assert "<title>Demo Page - Acme</title>" in out
    assert '<meta name="description" content="A demo">' in out
    assert '<link rel="stylesheet" href="/main.css">' in out
    assert '<script src="/main.js" defer></script>' in out


def test_html_head_escapes_unsafe_strings():
    out = html_head(
        title="<script>",
        site_name="Acme",
        description="x",
    )
    assert "<script>" not in out.replace("<script", "")
    assert "&lt;script&gt;" in out


def test_html_head_omits_google_fonts_when_unset():
    out = html_head(title="x", site_name="y", description="z")
    assert "fonts.googleapis.com" not in out


def test_html_head_emits_google_fonts_link_when_set():
    href = "https://fonts.googleapis.com/css2?family=Inter&display=swap"
    out = html_head(title="x", site_name="y", description="z", google_fonts_href=href)
    assert href in out
    assert "preconnect" in out


def test_html_head_extra_meta():
    out = html_head(
        title="x",
        site_name="y",
        description="z",
        extra_meta={"author": "Daisy"},
    )
    assert '<meta name="author" content="Daisy">' in out


def test_html_header_renders_with_subtitle_and_gradient():
    out = html_header(
        title="Heading",
        subtitle="Sub",
        theme_gradient="linear-gradient(0deg,#fff,#000)",
    )
    assert "<h1>Heading</h1>" in out
    assert "Sub" in out
    assert "linear-gradient" in out


def test_html_header_omits_update_date_when_disabled():
    out = html_header(title="X", show_update_date=False)
    assert "Updated " not in out


def test_navigation_includes_active_class():
    out = navigation([NavLink("/a.html", "A", active=False), NavLink("/b.html", "B", active=True)])
    assert '<a href="/a.html">A</a>' in out
    assert '<a href="/b.html" class="active">B</a>' in out


def test_navigation_empty_list_renders_empty_nav():
    out = navigation([])
    assert '<nav class="nav">' in out


def test_stat_grid_formats_integers_with_separator():
    out = stat_grid([("Total", 12345), ("Critical", 0)])
    assert "12,345" in out
    assert ">Total<" in out
    assert ">Critical<" in out


def test_section_grid_returns_empty_when_no_items():
    assert section_grid(title="By County", items=()) == ""


def test_section_grid_uses_supplied_classes():
    out = section_grid(
        title="By County",
        items=(("Miami-Dade", "miami-dade.html", 100),),
        item_class="county-link",
        count_class="county-count",
        container_class="county-grid",
    )
    assert 'class="county-link"' in out
    assert 'class="county-count"' in out
    assert 'class="county-grid"' in out
    assert "Miami-Dade" in out


def test_html_footer_emits_body_close():
    out = html_footer(inner_html="<!-- footer -->")
    assert "</body>" in out
    assert "</html>" in out


def test_legal_block_passes_html_through_verbatim():
    out = legal_block(html="<p>Disclaimer</p>")
    assert "<p>Disclaimer</p>" in out
