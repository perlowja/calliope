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

"""calliope.pages — page-level composition primitives.

Stage 3 ships substrate-shaped abstractions for page composition:

- ``Pagination``, ``PaginationPage``, ``paginate()`` — slice large
  collections into per-page streams.
- ``Hero``, ``render_hero()`` — above-the-fold section for landing pages.
- ``Scoreboard``, ``ScoreboardRow``, ``render_scoreboard()`` — titled
  tabular display with optional total.
- ``NarrativeRenderer`` Protocol + ``TemplateNarrativeRenderer`` —
  numeric-signals-to-prose adapter point. AI-driven narrative renderers
  belong in adapters, not in calliope.
- Canonical block-name tuples (``INDEX_PAGE_BLOCKS``, ``LIST_PAGE_BLOCKS``,
  ``DIMENSION_PAGE_BLOCKS``, ``DETAIL_PAGE_BLOCKS``) for use as
  ``TemplateMetadata.blocks``.

Concrete page generators live in adapters; calliope ships zero
domain-specific pages.

See ``docs/CALLIOPE-SPEC.md`` §10 for the contract.
"""

from calliope.pages.blocks import (
    DETAIL_PAGE_BLOCKS,
    DIMENSION_PAGE_BLOCKS,
    INDEX_PAGE_BLOCKS,
    LIST_PAGE_BLOCKS,
)
from calliope.pages.hero import Hero, render_hero
from calliope.pages.narrative import NarrativeRenderer, TemplateNarrativeRenderer
from calliope.pages.pagination import Pagination, PaginationPage, paginate
from calliope.pages.scoreboard import (
    Scoreboard,
    ScoreboardRow,
    make_scoreboard,
    render_scoreboard,
)

__all__ = [
    "DETAIL_PAGE_BLOCKS",
    "DIMENSION_PAGE_BLOCKS",
    "Hero",
    "INDEX_PAGE_BLOCKS",
    "LIST_PAGE_BLOCKS",
    "NarrativeRenderer",
    "Pagination",
    "PaginationPage",
    "Scoreboard",
    "ScoreboardRow",
    "TemplateNarrativeRenderer",
    "make_scoreboard",
    "paginate",
    "render_hero",
    "render_scoreboard",
]
