# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""Canonical page block-name sequences.

Calliope ships these as recommended `metadata.blocks` tuples for the
common page archetypes. They are conventions, not requirements:
adapters can define their own block sequences. Validating against a
canonical sequence makes cross-adapter pages consistent for downstream
tooling (block extraction, page-level diffing, accessibility checks).

The conventions match production cleanroom output where applicable
(`L1_metagenerator.py:1331-1369`).
"""

from __future__ import annotations

INDEX_PAGE_BLOCKS: tuple[str, ...] = (
    "head",
    "header",
    "nav",
    "hero",
    "scoreboard",
    "content",
    "footer",
)
"""Landing / index page: hero + scoreboard + free-form content."""

LIST_PAGE_BLOCKS: tuple[str, ...] = (
    "head",
    "header",
    "nav",
    "filters",
    "list",
    "pagination",
    "footer",
)
"""Paginated list page: optional filters + list + pagination controls."""

DIMENSION_PAGE_BLOCKS: tuple[str, ...] = (
    "head",
    "header",
    "nav",
    "how-to-use",
    "stats",
    "signup",
    "news",
    "content",
    "legal",
    "footer",
)
"""Per-dimension page from cleanroom production output.

Matches L1_metagenerator.py block sequence verbatim. Keep this tuple
stable so pages that lifted with this sequence can validate without
custom metadata.
"""

DETAIL_PAGE_BLOCKS: tuple[str, ...] = (
    "head",
    "header",
    "nav",
    "summary",
    "details",
    "related",
    "footer",
)
"""Single-item detail page: summary + details + related links."""
