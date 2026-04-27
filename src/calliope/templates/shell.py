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

"""Sanitized HTML shell helpers.

Lifted from upstream cleanroom `aedifex_template.py`. Domain coupling
(brand strings, dimension taxonomy, jurisdiction-specific text, theme
tables) has been stripped. Callers supply their own labels, navigation
items, legal copy, and shared-asset paths.

These are utility functions, not a `PageTemplate`. A `JinjaPageTemplate`
subclass may compose them in its template; a procedural renderer may call
them directly.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import NamedTuple

from calliope.templates.base import safe_value


class NavLink(NamedTuple):
    href: str
    label: str
    active: bool = False


def base_path(depth: int) -> str:
    """Relative path to site root from a page at `depth` directories deep.

    `depth=0` → `"."` (root), `depth=1` → `"../"`, `depth=2` → `"../../"`.
    """
    if depth < 0:
        raise ValueError(f"depth must be non-negative, got {depth}")
    if depth == 0:
        return "."
    return "../" * depth


def html_head(
    *,
    title: str,
    site_name: str,
    description: str,
    stylesheets: Sequence[str] = (),
    scripts: Sequence[str] = (),
    google_fonts_href: str | None = None,
    extra_meta: Mapping[str, str] = {},
) -> str:
    """Render `<!DOCTYPE html><html><head>...` through `</head>`.

    `stylesheets` and `scripts` are emitted in order. Scripts are rendered
    with `defer`. `extra_meta` is a `name=value` mapping for additional
    `<meta>` tags.
    """
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <meta name="description" content="{safe_value(description)}">',
        f'    <meta property="og:title" content="{safe_value(title)} - {safe_value(site_name)}">',
        f'    <meta property="og:description" content="{safe_value(description)}">',
        '    <meta property="og:type" content="website">',
        '    <meta name="twitter:card" content="summary">',
        f"    <title>{safe_value(title)} - {safe_value(site_name)}</title>",
    ]
    for name, value in extra_meta.items():
        parts.append(f'    <meta name="{safe_value(name)}" content="{safe_value(value)}">')
    if google_fonts_href:
        parts.extend(
            [
                '    <link rel="preconnect" href="https://fonts.googleapis.com">',
                '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
                f'    <link href="{google_fonts_href}" rel="stylesheet">',
            ]
        )
    for href in stylesheets:
        parts.append(f'    <link rel="stylesheet" href="{href}">')
    for src in scripts:
        parts.append(f'    <script src="{src}" defer></script>')
    parts.append("</head>")
    return "\n".join(parts)


def html_header(
    *,
    title: str,
    subtitle: str = "",
    theme_gradient: str = "",
    show_update_date: bool = True,
    update_date_fmt: str = "%b %d, %Y %I:%M %p",
) -> str:
    style = f' style="background: {theme_gradient};"' if theme_gradient else ""
    update = ""
    if show_update_date:
        when = datetime.now().strftime(update_date_fmt)
        update = f'\n        <div class="update-date">Updated {safe_value(when)}</div>'
    sub = f'\n        <div class="subtitle">{safe_value(subtitle)}</div>' if subtitle else ""
    return (
        "\n<body>\n"
        f'    <div class="header"{style}>\n'
        f"        <h1>{safe_value(title)}</h1>"
        f"{sub}"
        f"{update}\n"
        "    </div>"
    )


def navigation(links: Sequence[NavLink]) -> str:
    items = []
    for link in links:
        cls = ' class="active"' if link.active else ""
        items.append(f'        <a href="{link.href}"{cls}>{safe_value(link.label)}</a>')
    inner = "\n".join(items) if items else ""
    return f'\n    <nav class="nav">\n{inner}\n    </nav>'


def stat_grid(stats: Sequence[tuple[str, object]]) -> str:
    """Render a row of `(label, value)` stat cards.

    Numeric values are formatted with thousands separators by `safe_value`.
    """
    cards = []
    for label, value in stats:
        cards.append(
            '        <div class="stat-card">\n'
            f'            <div class="stat-value">{safe_value(value)}</div>\n'
            f'            <div class="stat-label">{safe_value(label)}</div>\n'
            "        </div>"
        )
    inner = "\n".join(cards) if cards else ""
    return f'\n    <div class="stats-grid">\n{inner}\n    </div>'


def section_grid(
    *,
    title: str,
    items: Sequence[tuple[str, str, int]],
    item_class: str = "section-link",
    count_class: str = "section-count",
    container_class: str = "section-grid",
) -> str:
    """Render a titled grid of `(label, href, count)` links.

    Replaces the cleanroom `get_county_grid` helper without the
    jurisdiction-specific assumption.
    """
    if not items:
        return ""
    rendered = []
    for label, href, count in items:
        rendered.append(
            f'            <a href="{href}" class="{item_class}">\n'
            f"                <span>{safe_value(label)}</span>\n"
            f'                <span class="{count_class}">{safe_value(int(count))}</span>\n'
            "            </a>"
        )
    inner = "\n".join(rendered)
    return (
        f'\n        <h2 class="section-title">{safe_value(title)}</h2>\n'
        f'        <div class="{container_class}">\n{inner}\n        </div>'
    )


def html_footer(*, footer_class: str = "footer", inner_html: str = "") -> str:
    """Render `</body></html>` with a footer container.

    `inner_html` is inserted verbatim (no escaping). Callers building a
    footer from user-supplied data should escape upstream.
    """
    return f'\n    <div class="{footer_class}">\n        {inner_html}\n    </div>\n</body>\n</html>'


def legal_block(*, html: str, block_class: str = "legal-block") -> str:
    """Inline legal disclaimer block.

    `html` is verbatim — calliope does not ship jurisdiction-specific copy.
    """
    return f'\n        <div class="{block_class}">\n{html}\n        </div>'
