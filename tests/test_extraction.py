# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from calliope.templates import extract_blocks


def test_extract_blocks_returns_inner_content(production_page):
    blocks = extract_blocks(production_page, ["header", "footer"])
    assert "Header content" in blocks["header"]
    assert "Site footer" in blocks["footer"]


def test_extract_blocks_handles_kebab_case_with_annotation(production_page):
    blocks = extract_blocks(production_page, ["how-to-use", "signup"])
    assert "How to use" in blocks["how-to-use"]
    assert "signup-placeholder" in blocks["signup"]


def test_extract_blocks_skips_annotation_in_inner_content():
    html = "<!-- BLOCK:foo (a hint - with hyphen) -->INNER<!-- /BLOCK:foo -->"
    blocks = extract_blocks(html, ["foo"])
    assert blocks["foo"] == "INNER"


def test_extract_blocks_returns_empty_for_missing_block():
    blocks = extract_blocks("<html></html>", ["header"])
    assert blocks["header"] == ""


def test_extract_blocks_default_returns_all_paired_blocks(production_page):
    blocks = extract_blocks(production_page)
    assert {
        "header",
        "nav",
        "how-to-use",
        "stats",
        "signup",
        "news",
        "content",
        "legal",
        "footer",
    }.issubset(blocks)


def test_extract_blocks_skips_unclosed():
    html = "<!-- BLOCK:foo --> never closes"
    blocks = extract_blocks(html)
    assert blocks == {}


def test_extract_blocks_returns_empty_for_duplicate_name():
    html = """
    <!-- BLOCK:x -->outer
    <!-- BLOCK:x -->inner<!-- /BLOCK:x -->
    <!-- /BLOCK:x -->
    """
    blocks = extract_blocks(html, ["x"])
    assert blocks["x"] == ""


def test_extract_blocks_returns_empty_for_repeated_name_at_same_level():
    html = "<!-- BLOCK:x -->A<!-- /BLOCK:x --><!-- BLOCK:x -->B<!-- /BLOCK:x -->"
    blocks = extract_blocks(html, ["x"])
    assert blocks["x"] == ""
