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

"""Heatbar — segmented colored bar visualizing a composite score.

The cleanroom heatbar showed a v2.0 score split across HP / INT / BAS / Pest
contributions. Calliope generalizes: callers describe their segments by
`(weight, css_class, color, title)`. The rendered bar's total width is
`fill_pct` of the container; segments split that width by weight.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from calliope.templates import safe_value


@dataclass(frozen=True)
class HeatbarSegment:
    weight: float
    css_class: str = ""
    color: str | None = None
    title: str | None = None


def render_heatbar(
    segments: Iterable[HeatbarSegment],
    *,
    fill_pct: float,
    container_class: str = "heatbar",
    title: str | None = None,
) -> str:
    """Render a colored bar that fills `fill_pct` percent of its container.

    `fill_pct` is clamped to [0, 100]. Segments with non-finite weight or
    `weight <= 0` are skipped. If all segments have zero or non-finite
    weight, an empty string is returned.
    """
    if fill_pct <= 0:
        return ""
    fill_pct = min(100.0, max(0.0, fill_pct))

    segs = [s for s in segments if math.isfinite(s.weight) and s.weight > 0]
    total_weight = sum(s.weight for s in segs)
    if total_weight <= 0:
        return ""

    title_attr = f' title="{safe_value(title)}"' if title else ""
    parts: list[str] = [f'<div class="{container_class}"{title_attr}>']
    for seg in segs:
        seg_pct = (seg.weight / total_weight) * fill_pct
        classes = f"{container_class}-segment"
        if seg.css_class:
            classes = f"{classes} {seg.css_class}"
        style = f"width:{seg_pct:.1f}%;"
        if seg.color:
            style += f"background:{seg.color};"
        seg_title = f' title="{safe_value(seg.title)}"' if seg.title else ""
        parts.append(f'<div class="{classes}" style="{style}"{seg_title}></div>')
    parts.append("</div>")
    return "".join(parts)
