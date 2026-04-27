# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from calliope.templates import (
    CLOSE_RE,
    OPEN_RE,
    ComplianceLevel,
    detect_blocks,
    extract_blocks,
    validate_output,
)


def test_open_re_matches_simple_marker():
    m = OPEN_RE.search("<!-- BLOCK:header -->")
    assert m is not None
    assert m.group("name") == "header"
    assert (m.group("annotation") or "") == ""


def test_open_re_matches_kebab_case_name():
    m = OPEN_RE.search("<!-- BLOCK:how-to-use -->")
    assert m is not None
    assert m.group("name") == "how-to-use"


def test_open_re_matches_annotated_marker():
    m = OPEN_RE.search("<!-- BLOCK:signup (placeholder for MailerLite - prevents layout shift) -->")
    assert m is not None
    assert m.group("name") == "signup"
    assert "MailerLite" in (m.group("annotation") or "")


def test_open_re_matches_paren_annotation_with_hyphen_inside():
    m = OPEN_RE.search("<!-- BLOCK:how-to-use (placeholder - prevents layout shift) -->")
    assert m is not None
    assert m.group("name") == "how-to-use"


def test_close_re_matches():
    m = CLOSE_RE.search("<!-- /BLOCK:how-to-use -->")
    assert m is not None
    assert m.group("name") == "how-to-use"


def test_close_re_does_not_match_open():
    assert CLOSE_RE.search("<!-- BLOCK:header -->") is None


def test_detect_blocks_on_production_fixture(production_page, production_block_order):
    found = detect_blocks(production_page)
    assert found == production_block_order


def test_validate_full_compliance_on_production_fixture(production_page, production_block_order):
    result = validate_output(production_page, production_block_order)
    assert result.level is ComplianceLevel.FULL
    assert result.is_compliant
    assert result.is_usable
    assert result.found_blocks == production_block_order
    assert result.missing_blocks == ()
    assert result.extra_blocks == ()
    assert result.out_of_order == ()
    assert result.unclosed_blocks == ()


def test_validate_detects_missing_block(production_page, production_block_order):
    expected = production_block_order + ("not-rendered",)
    result = validate_output(production_page, expected)
    assert result.level is ComplianceLevel.PARTIAL
    assert "not-rendered" in result.missing_blocks


def test_validate_detects_extra_block(production_page):
    expected = ("header",)
    result = validate_output(production_page, expected)
    assert result.level is ComplianceLevel.PARTIAL
    assert "nav" in result.extra_blocks


def test_validate_detects_out_of_order():
    html = """
    <!-- BLOCK:b -->x<!-- /BLOCK:b -->
    <!-- BLOCK:a -->x<!-- /BLOCK:a -->
    """
    result = validate_output(html, ("a", "b"))
    assert result.level is ComplianceLevel.PARTIAL
    assert result.out_of_order != ()


def test_validate_detects_unclosed_block():
    html = "<!-- BLOCK:header --> oops <!-- BLOCK:footer --><!-- /BLOCK:footer -->"
    result = validate_output(html, ("header", "footer"))
    assert "header" in result.unclosed_blocks
    assert result.level is ComplianceLevel.PARTIAL


def test_validate_requires_close_after_open_and_matches_extraction():
    html = "<!-- /BLOCK:header --><!-- BLOCK:header -->late content"
    result = validate_output(html, ("header",))
    assert result.found_blocks == ()
    assert result.unclosed_blocks == ("header",)
    assert result.level is ComplianceLevel.PARTIAL
    assert detect_blocks(html) == ()
    assert extract_blocks(html, ["header"])["header"] == ""


def test_validate_classifies_nested_same_name_as_partial_duplicate():
    html = """
    <!-- BLOCK:header -->outer
    <!-- BLOCK:header -->inner<!-- /BLOCK:header -->
    <!-- /BLOCK:header -->
    """
    result = validate_output(html, ("header",))
    assert result.level is ComplianceLevel.PARTIAL
    assert result.is_usable
    assert not result.is_compliant
    assert result.found_blocks == ()
    assert result.missing_blocks == ("header",)
    assert result.extra_blocks == ()
    assert result.duplicate_blocks == ("header",)
    assert result.out_of_order == ()
    assert result.unclosed_blocks == ()


def test_validate_returns_none_when_no_markers():
    result = validate_output("<html><body>nothing here</body></html>", ("header",))
    assert result.level is ComplianceLevel.NONE
    assert not result.is_compliant
    assert not result.is_usable


def test_validate_ignores_close_only_markers():
    html = "<!-- /BLOCK:header --> stuff"
    result = validate_output(html, ("header",))
    assert result.level is ComplianceLevel.NONE


def test_validate_passes_through_data_warnings(production_page, production_block_order):
    warnings = ("missing optional 'description'",)
    result = validate_output(production_page, production_block_order, data_warnings=warnings)
    assert result.data_warnings == warnings
