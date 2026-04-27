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

"""Pill — small label-style badge rendered inline in a card.

A `Pill` is a `(label, css_class, color)` triple. The cleanroom rendered
several pill variants from per-domain dicts; calliope decouples the data
shape (`TaxonomyEntry`) from the visual element (`Pill`) so callers can
construct pills from any source.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from calliope.cards.taxonomy import TaxonomyEntry
from calliope.templates import safe_value


@dataclass(frozen=True)
class Pill:
    label: str
    css_class: str = ""
    color: str | None = None
    title: str | None = None

    @classmethod
    def from_taxonomy(cls, entry: TaxonomyEntry, *, title: str | None = None) -> Pill:
        return cls(label=entry.label, css_class=entry.css_class, color=entry.color, title=title)


def render_pill(pill: Pill, *, base_class: str = "pill") -> str:
    classes = base_class
    if pill.css_class:
        classes = f"{base_class} {pill.css_class}"
    style = f' style="background:{pill.color};"' if pill.color else ""
    title = f' title="{safe_value(pill.title)}"' if pill.title else ""
    return f'<span class="{classes}"{style}{title}>{safe_value(pill.label)}</span>'


def render_pills(
    pills: Iterable[Pill],
    *,
    container_class: str = "pills",
    base_class: str = "pill",
) -> str:
    rendered = [render_pill(p, base_class=base_class) for p in pills]
    if not rendered:
        return ""
    return f'<div class="{container_class}">{" ".join(rendered)}</div>'
