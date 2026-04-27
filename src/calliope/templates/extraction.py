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

"""Parser-based block extraction.

Uses the marker scanner from `validation` rather than exact-string search,
so hyphenated names and annotated openings extract the right span.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from calliope.templates.validation import _match_blocks


def extract_blocks(html: str, names: Iterable[str] | None = None) -> Mapping[str, str]:
    """Return {block_name: inner_content} for each requested block.

    `names=None` extracts every block whose opening marker has a matching
    closing marker, except duplicate opening names which are intentionally
    not extracted. Inner content is verbatim (whitespace preserved, leading
    and trailing newlines stripped to one).
    """
    wanted: set[str] | None = set(names) if names is not None else None

    out: dict[str, str] = {}
    for match in _match_blocks(html):
        name = match.open_span.name
        if wanted is not None and name not in wanted:
            continue
        if name in out:
            continue
        inner = html[match.open_span.end : match.close_span.start]
        out[name] = inner.strip("\n")
    if wanted is not None:
        for name in wanted:
            out.setdefault(name, "")
    return out
