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

"""Scoreboard — a titled tabular display of `(label, count)` rows.

The cleanroom rendered "metro scoreboards" with hardcoded Florida metros;
calliope generalizes: rows are caller-supplied `ScoreboardRow` tuples.
The optional total row sums the counts.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from calliope.pages._validation import (
    validate_class_list,
    validate_css_declaration_value,
)
from calliope.templates import safe_value


@dataclass(frozen=True)
class ScoreboardRow:
    label: str
    count: int = 0
    href: str | None = None
    color: str | None = None
    css_class: str = ""

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValueError(f"ScoreboardRow.count must be >= 0 (row label={self.label!r})")
        validate_css_declaration_value(self.color, field_name="color")
        validate_class_list(self.css_class, field_name="css_class")


@dataclass(frozen=True)
class Scoreboard:
    title: str
    rows: tuple[ScoreboardRow, ...]
    total_label: str = "TOTAL"
    show_total: bool = True
    container_class: str = "scoreboard"

    def __post_init__(self) -> None:
        validate_class_list(self.container_class, field_name="container_class")
        if not isinstance(self.rows, tuple):
            raise TypeError("Scoreboard.rows must be a tuple")
        for row in self.rows:
            if not isinstance(row, ScoreboardRow):
                raise TypeError(
                    f"Scoreboard.rows entries must be ScoreboardRow, got {type(row).__name__}"
                )

    @property
    def total(self) -> int:
        return sum(row.count for row in self.rows)


def make_scoreboard(
    title: str,
    rows: Iterable[ScoreboardRow],
    *,
    total_label: str = "TOTAL",
    show_total: bool = True,
    container_class: str = "scoreboard",
) -> Scoreboard:
    return Scoreboard(
        title=title,
        rows=tuple(rows),
        total_label=total_label,
        show_total=show_total,
        container_class=container_class,
    )


def render_scoreboard(scoreboard: Scoreboard) -> str:
    """Render a `<section class="scoreboard">…</section>` block.

    Empty scoreboards (no rows) still render the title and total (=0).
    """
    parts: list[str] = [
        "<!-- BLOCK:scoreboard -->",
        f'    <section class="{safe_value(scoreboard.container_class)}">',
        f'        <h2 class="scoreboard-title">{safe_value(scoreboard.title)}</h2>',
        '        <div class="scoreboard-rows">',
    ]
    for row in scoreboard.rows:
        classes = "scoreboard-row"
        if row.css_class:
            classes = f"{classes} {row.css_class}"
        classes_attr = safe_value(classes)
        style = f' style="background:{row.color};"' if row.color else ""
        label_html = safe_value(row.label)
        count_html = safe_value(row.count)
        if row.href:
            parts.append(
                f'            <a href="{safe_value(row.href)}" class="{classes_attr}"{style}>'
                f"<span>{label_html}</span><strong>{count_html}</strong></a>"
            )
        else:
            parts.append(
                f'            <div class="{classes_attr}"{style}>'
                f"<span>{label_html}</span><strong>{count_html}</strong></div>"
            )
    parts.append("        </div>")

    if scoreboard.show_total:
        parts.append(
            '        <div class="scoreboard-total">'
            f"<span>{safe_value(scoreboard.total_label)}</span>"
            f"<strong>{safe_value(scoreboard.total)}</strong></div>"
        )

    parts.append("    </section>")
    parts.append("<!-- /BLOCK:scoreboard -->")
    return "\n".join(parts)
