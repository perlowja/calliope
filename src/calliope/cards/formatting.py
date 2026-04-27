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

"""Pure utility formatters lifted (sanitized) from cleanroom cards.

`format_iso_date` and `slugify` are domain-agnostic. The cleanroom's
`parse_file_date` (Sunbiz `MMDDYYYY` format) and `calculate_business_age`
(Sunbiz-derived) stay in the RiskyEats slim adapter — they encode a
specific data source's quirks.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any

_SLUG_NON_ALPHANUM_RE = re.compile(r"[^a-z0-9]+")
_SLUG_TRAILING_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+$")


def _strip_separator_runs(text: str, separator: str) -> str:
    if not separator:
        return text
    pattern = re.compile(rf"^(?:{re.escape(separator)})+|(?:{re.escape(separator)})+$")
    return pattern.sub("", text)


def format_iso_date(value: Any, *, default: str = "") -> str:
    """Format a value as `YYYY-MM-DD`.

    Accepts `datetime`, `date`, ISO-8601 strings (truncated to first 10
    chars), or anything `str()` can render. Returns `default` for `None`
    or empty values.
    """
    if value is None:
        return default
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value)
    if not text:
        return default
    return text[:10]


def slugify(text: str, *, separator: str = "-", max_length: int | None = None) -> str:
    """Lowercase, ASCII-fold, replace non-alphanumeric runs with `separator`.

    Idempotent; `slugify(slugify(x)) == slugify(x)`. Leading and trailing
    separator runs are removed from the final slug. Returns the empty
    string for input that produces no slug characters. Negative
    `max_length` raises `ValueError`; `max_length=0` returns `""`.
    """
    if max_length is not None and max_length < 0:
        raise ValueError("slugify.max_length must be >= 0")
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    replaced = _SLUG_NON_ALPHANUM_RE.sub(separator, lowered)
    trimmed = _strip_separator_runs(replaced, separator)
    if max_length is not None and len(trimmed) > max_length:
        trimmed = trimmed[:max_length]
        trimmed = _SLUG_TRAILING_NON_ALNUM_RE.sub("", trimmed)
    return trimmed
