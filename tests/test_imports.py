# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""Smoke test — every subpackage imports cleanly.

Phase 7 Stage 0 baseline. Subsequent stages add real primitive tests
under tests/test_<subpackage>.py.
"""

from __future__ import annotations


def test_top_level_package_imports():
    import calliope

    assert calliope.__version__ == "0.0.1rc1"


def test_subpackages_import():
    """Every subpackage must be importable from a clean install."""
    import calliope.assets  # noqa: F401
    import calliope.cards  # noqa: F401
    import calliope.deploy  # noqa: F401
    import calliope.pages  # noqa: F401
    import calliope.render  # noqa: F401
    import calliope.templates  # noqa: F401
