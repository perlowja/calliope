# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Smoke test — every subpackage imports cleanly + key API is exported."""

from __future__ import annotations


def test_top_level_package_imports():
    import calliope

    assert calliope.__version__ == "0.0.2"


def test_subpackages_import():
    import calliope.assets  # noqa: F401
    import calliope.cards  # noqa: F401
    import calliope.deploy  # noqa: F401
    import calliope.pages  # noqa: F401
    import calliope.render  # noqa: F401
    import calliope.templates  # noqa: F401


def test_templates_public_surface():
    from calliope import templates

    expected = {
        "CLOSE_RE",
        "ComplianceLevel",
        "JinjaPageTemplate",
        "OPEN_RE",
        "PageTemplate",
        "TemplateMetadata",
        "TemplateRegistry",
        "ValidationResult",
        "bind_data",
        "detect_blocks",
        "extract_blocks",
        "safe_value",
        "validate_output",
    }
    assert expected.issubset(set(templates.__all__))
    for name in expected:
        assert hasattr(templates, name), f"missing export: {name!r}"


def test_render_exports_render_result():
    from calliope.render import RenderResult

    assert RenderResult.__name__ == "RenderResult"


def test_public_docstrings_are_domain_neutral_and_stage_current():
    import calliope
    import calliope.render

    combined = "\n".join((calliope.__doc__ or "", calliope.render.__doc__ or ""))
    for forbidden in ("RiskyEats", "DBPR", "restaurant", "chronic", "redalert"):
        assert forbidden not in combined
    assert "Stage 0" not in (calliope.__doc__ or "")
    assert "Phase 7 Stage 1" in (calliope.__doc__ or "")
