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

"""Validation helpers shared by page primitives.

These helpers provide **defense-in-depth** for caller-supplied values that
flow into HTML attributes and `style="..."` declarations. They are not a
substitute for upstream sanitization: see `docs/CALLIOPE-SPEC.md` §13 for
calliope's security posture.

The HTML-entity check uses `html.unescape()` against Python's full HTML5
entity table, so legacy named entities like `&quot` (without trailing
`;`) are caught alongside their modern `&quot;` form, decimal references
(`&#34;`), and hex references (`&#x22;`). Plain ampersands followed by
query-string parameters (e.g. `?x=1&y=2`) survive because they decode
unchanged.
"""

from __future__ import annotations

import html
import re

_CLASS_LIST_RE = re.compile(r"[A-Za-z0-9_-]+(?: [A-Za-z0-9_-]+)*\Z")
_CSS_ATTRIBUTE_UNSAFE_CHARS = frozenset({'"', "'", "\n", "\r"})


def _has_attribute_break(value: str) -> bool:
    """True if the HTML-decoded value contains chars that escape a quoted
    attribute or inject a CSS declaration boundary."""
    decoded = html.unescape(value)
    return any(ch in _CSS_ATTRIBUTE_UNSAFE_CHARS for ch in decoded)


def validate_class_list(value: str, *, field_name: str) -> str:
    """Validate a space-separated class list used in HTML attributes."""
    if not value:
        return value
    if html.unescape(value) != value:
        raise ValueError(
            f"{field_name} contains HTML entity references not allowed in a class list"
        )
    if _CLASS_LIST_RE.fullmatch(value):
        return value
    raise ValueError(
        f"{field_name} must contain only letters, numbers, underscores, hyphens, and single spaces"
    )


def validate_css_attribute_value(value: str | None, *, field_name: str) -> str | None:
    """Validate a CSS fragment embedded inside `style="..."`.

    Rejects raw or HTML-entity-encoded quote characters and newlines
    that could escape the attribute. The check uses Python's HTML5
    entity table via `html.unescape()`, so legacy named references
    (e.g. `&quot` without `;`) are caught alongside their fully-formed
    counterparts.
    """
    if value is None or value == "":
        return value
    if _has_attribute_break(value):
        raise ValueError(f"{field_name} contains unsafe characters for CSS attribute context")
    return value


def validate_css_declaration_value(value: str | None, *, field_name: str) -> str | None:
    """Validate a raw CSS declaration value embedded in `style="..."`.

    Stricter than `validate_css_attribute_value`: also rejects `;` (the
    CSS declaration separator) in both raw and HTML-entity-encoded form.
    """
    if value is None or value == "":
        return value
    decoded = html.unescape(value)
    if any(ch in _CSS_ATTRIBUTE_UNSAFE_CHARS for ch in decoded):
        raise ValueError(f"{field_name} contains unsafe characters for CSS declaration context")
    if ";" in decoded:
        raise ValueError(f"{field_name} contains unsafe characters for CSS declaration context")
    return value
