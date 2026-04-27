# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.cards — per-row card renderers.

Status: stub. Phase 7 Stage 1 lifts the cleanroom's card_components
family into this package.

Source files staged for lift (parent: ``riskyeats-cleanroom/src/``):

    card_components.py              (1887 LOC) — base card renderer
    badactors_card_components.py    ( 660 LOC) — bad-actors variant
    codered_card_components.py      ( 866 LOC) — code-red variant
    codered_card_components_v2.py   ( 560 LOC) — code-red v2
    defunct_card_components.py      ( 896 LOC) — defunct variant

Planned Protocol:

    CardRenderer.render(row: dict[str, Any]) -> str
        Returns rendered HTML for a single row.
    CardRenderer.required_columns() -> set[str]
        What the row must contain to render meaningfully.

Concrete implementations register themselves so apps can pick a
renderer by name from the manifest.
"""
