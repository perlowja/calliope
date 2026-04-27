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

"""calliope.render — render drivers and dimension-oriented page runners.

Stage 1 lands `RenderResult` here so render drivers can produce results
without `templates/` importing render-stage concerns. Subsequent stages
add the parallel and production drivers + per-dimension runners.

Source files staged for lift (~15 files):

    Drivers:
        L1_render_parallel.py       (297 LOC) — parallel batched render
        L1_render_static_pro.py     (172 LOC) — production static
                                                renderer

    Dimension generators:
        L1_*_generator.py family (dimension-specific page runners)

Planned shape: each per-dimension generator becomes a
`DimensionRenderer` instance — configured with a card variant
(calliope.cards) + a page template (calliope.templates) + a row
filter / sort. Apps register dimensions by name in their manifest;
the parallel driver runs every registered dimension in parallel.
"""

from calliope.render.job import RenderJob
from calliope.render.protocol import Renderable, RenderDriver
from calliope.render.report import JobOutcome, RenderReport
from calliope.render.results import RenderResult
from calliope.render.serial import SerialRenderDriver
from calliope.render.threaded import ThreadedRenderDriver

__all__ = [
    "JobOutcome",
    "RenderDriver",
    "RenderJob",
    "RenderReport",
    "RenderResult",
    "Renderable",
    "SerialRenderDriver",
    "ThreadedRenderDriver",
]
