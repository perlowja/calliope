# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.render — render drivers + per-dimension page runners.

Status: stub. Phase 7 Stage 4 lifts the cleanroom's render drivers
+ per-dimension generators into this package.

Source files staged for lift (~15 files):

    Drivers:
        L1_render_parallel.py       (297 LOC) — parallel batched render
        L1_render_static_pro.py     (172 LOC) — production static
                                                renderer

    Per-dimension generators:
        L1_badactors_generator.py
        L1_chronic_generator.py
        L1_cleanplates_generator.py
        L1_code_red_generator.py
        L1_condition_green_generator.py
        L1_defunct_generator.py
        L1_ghost_generator.py
        L1_hotspots_generator.py
        L1_mobilebusiness_generator.py
        L1_nearmiss_generator.py
        L1_newopenings_generator.py
        L1_permanent_generator.py
        L1_redalert_generator.py

Planned shape: each per-dimension generator becomes a
`DimensionRenderer` instance — configured with a card variant
(calliope.cards) + a page template (calliope.templates) + a row
filter / sort. Apps register dimensions by name in their manifest;
the parallel driver runs every registered dimension in parallel.
"""
