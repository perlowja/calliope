# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.pages — page-level generators.

Status: stub. Phase 7 Stage 3 lifts the cleanroom's L-stage page
generators into this package.

Source files staged for lift:

    L1_landing_generator.py       (1745 LOC) — landing page
    L1_metagenerator.py           (1998 LOC) — multi-page driver
    L1_analytics_generator.py     (1024 LOC) — primary analytics page
    L1_narrative.py                          — narrative-text composer

Planned shape: pages compose cards (calliope.cards) into final HTML
documents via templates (calliope.templates) and reference assets
(calliope.assets). Multi-page output uses the metagenerator pattern
to produce per-county / per-metro variants from a single config.
"""
