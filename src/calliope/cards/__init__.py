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

"""calliope.cards — per-row card renderers.

Stage 2 ships the substrate primitives:

- ``CardRenderer`` Protocol (swappable contract).
- ``CardTemplate`` ABC + ``JinjaCardTemplate`` (concrete base).
- ``Taxonomy`` / ``TaxonomyEntry`` (domain key → display attrs).
- ``Pill`` and renderers (inline label badges).
- ``HeatbarSegment`` and renderer (segmented colored bar).
- ``Tier`` / ``TierTable`` (score-to-label classification).
- Pure formatters: ``format_iso_date``, ``slugify``.

Concrete domain card variants (e.g. inspection cards, listing cards)
live in adapters; calliope ships zero domain-specific taxonomy data.

See ``docs/CALLIOPE-SPEC.md`` §9 for the contract.
"""

from calliope.cards.base import CardTemplate, JinjaCardTemplate
from calliope.cards.formatting import format_iso_date, slugify
from calliope.cards.heatbar import HeatbarSegment, render_heatbar
from calliope.cards.pill import Pill, render_pill, render_pills
from calliope.cards.protocol import CardRenderer
from calliope.cards.taxonomy import Taxonomy, TaxonomyEntry
from calliope.cards.tier import Tier, TierTable, make_tier_table

__all__ = [
    "CardRenderer",
    "CardTemplate",
    "HeatbarSegment",
    "JinjaCardTemplate",
    "Pill",
    "Taxonomy",
    "TaxonomyEntry",
    "Tier",
    "TierTable",
    "format_iso_date",
    "make_tier_table",
    "render_heatbar",
    "render_pill",
    "render_pills",
    "slugify",
]
