# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from calliope.assets import AssetManifest, rewrite_html_with_manifest


def test_rewrite_replaces_href():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    out = rewrite_html_with_manifest('<link href="main.css">', m)
    assert out == '<link href="main.abcd.css">'


def test_rewrite_replaces_src():
    m = AssetManifest(entries={"app.js": "app.efgh.js"})
    out = rewrite_html_with_manifest('<script src="app.js"></script>', m)
    assert 'src="app.efgh.js"' in out


def test_rewrite_replaces_css_url():
    m = AssetManifest(entries={"font.woff2": "font.deadbeef.woff2"})
    out = rewrite_html_with_manifest("body { background: url('font.woff2'); }", m)
    assert "url('font.deadbeef.woff2')" in out


def test_rewrite_handles_dot_slash_prefix():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    out = rewrite_html_with_manifest('<link href="./main.css">', m)
    assert 'href="./main.abcd.css"' in out


def test_rewrite_leaves_unknown_paths_unchanged():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    out = rewrite_html_with_manifest(
        '<link href="not-in-manifest.css"><link href="main.css">',
        m,
    )
    assert 'href="not-in-manifest.css"' in out
    assert 'href="main.abcd.css"' in out


def test_rewrite_with_base_path():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    out = rewrite_html_with_manifest(
        '<link href="/static/main.css">',
        m,
        base_path="/static/",
    )
    assert 'href="/static/main.abcd.css"' in out


def test_rewrite_with_base_path_falls_back_to_unprefixed():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    # When the input doesn't have the base_path, also try the bare match.
    out = rewrite_html_with_manifest(
        '<link href="main.css">',
        m,
        base_path="/static/",
    )
    assert 'href="/static/main.abcd.css"' in out


def test_rewrite_handles_double_quoted_and_single_quoted_attributes():
    m = AssetManifest(entries={"a.css": "a.1.css", "b.css": "b.2.css"})
    out = rewrite_html_with_manifest(
        """<link href="a.css"><link href='b.css'>""",
        m,
    )
    assert 'href="a.1.css"' in out
    assert "href='b.2.css'" in out


def test_rewrite_does_not_match_partial_filename():
    """Ensure substring matches in a longer filename are not rewritten."""
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    out = rewrite_html_with_manifest('<link href="superduper-main.css">', m)
    assert 'href="superduper-main.css"' in out  # unchanged


def test_rewrite_empty_manifest_is_identity():
    m = AssetManifest()
    html = '<link href="main.css">'
    assert rewrite_html_with_manifest(html, m) == html
