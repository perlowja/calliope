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

"""Marker grammar, structural validation, compliance levels.

The marker grammar accepts the production shape used in upstream cleanroom
output: kebab-case names and optional annotations on opening markers.
"""

from __future__ import annotations

import re
from collections import Counter, deque
from collections.abc import Collection, Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple

NAME_RE = r"[a-z][a-z0-9-]*"

OPEN_RE = re.compile(rf"<!--\s*BLOCK:(?P<name>{NAME_RE})(?:\s+(?P<annotation>[^>]*?))?\s*-->")
CLOSE_RE = re.compile(rf"<!--\s*/BLOCK:(?P<name>{NAME_RE})\s*-->")


class ComplianceLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class MarkerSpan(NamedTuple):
    name: str
    start: int
    end: int
    annotation: str | None


@dataclass(frozen=True)
class ValidationResult:
    level: ComplianceLevel
    found_blocks: tuple[str, ...]
    missing_blocks: tuple[str, ...] = ()
    extra_blocks: tuple[str, ...] = ()
    out_of_order: tuple[str, ...] = ()
    duplicate_blocks: tuple[str, ...] = ()
    unclosed_blocks: tuple[str, ...] = ()
    data_warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_compliant(self) -> bool:
        return self.level is ComplianceLevel.FULL

    @property
    def is_usable(self) -> bool:
        return self.level is not ComplianceLevel.NONE


def _scan_open(html: str) -> list[MarkerSpan]:
    return [
        MarkerSpan(
            name=m.group("name"),
            start=m.start(),
            end=m.end(),
            annotation=(m.group("annotation") or None),
        )
        for m in OPEN_RE.finditer(html)
    ]


def _scan_close(html: str) -> list[MarkerSpan]:
    return [
        MarkerSpan(name=m.group("name"), start=m.start(), end=m.end(), annotation=None)
        for m in CLOSE_RE.finditer(html)
    ]


class MatchedBlock(NamedTuple):
    open_span: MarkerSpan
    close_span: MarkerSpan


def _duplicate_open_names(opens: Iterable[MarkerSpan]) -> set[str]:
    counts = Counter(open_span.name for open_span in opens)
    return {name for name, count in counts.items() if count > 1}


def _match_blocks_from_spans(
    opens: Iterable[MarkerSpan],
    closes: Iterable[MarkerSpan],
    *,
    duplicate_names: Collection[str] = (),
) -> tuple[MatchedBlock, ...]:
    open_spans = tuple(opens)
    duplicate_names = set(duplicate_names) or _duplicate_open_names(open_spans)

    closes_by_name: dict[str, deque[MarkerSpan]] = {}
    for close in closes:
        closes_by_name.setdefault(close.name, deque()).append(close)

    matched: list[MatchedBlock] = []
    for open_span in open_spans:
        if open_span.name in duplicate_names:
            continue
        candidates = closes_by_name.get(open_span.name)
        if not candidates:
            continue
        while candidates and candidates[0].start < open_span.end:
            candidates.popleft()
        if not candidates:
            continue
        matched.append(MatchedBlock(open_span=open_span, close_span=candidates.popleft()))
    return tuple(matched)


def _match_blocks(html: str) -> tuple[MatchedBlock, ...]:
    opens = _scan_open(html)
    return _match_blocks_from_spans(
        opens,
        _scan_close(html),
        duplicate_names=_duplicate_open_names(opens),
    )


def detect_blocks(html: str) -> tuple[str, ...]:
    """Names of blocks that have a paired opening and closing marker, in
    document order of their opening marker.

    Duplicate-named opens (multiplicity > 1) are suppressed from the result,
    consistent with `extract_blocks()` and `validate_output().found_blocks`.
    Use `validate_output(...).duplicate_blocks` to recover those names.
    """
    return tuple(match.open_span.name for match in _match_blocks(html))


def validate_output(
    html: str,
    expected_blocks: Iterable[str],
    data_warnings: Iterable[str] = (),
) -> ValidationResult:
    expected = tuple(expected_blocks)
    opens = _scan_open(html)
    open_names = [m.name for m in opens]
    duplicate_names = _duplicate_open_names(opens)
    matched = _match_blocks_from_spans(opens, _scan_close(html), duplicate_names=duplicate_names)
    matched_opens = {match.open_span for match in matched}

    found = tuple(match.open_span.name for match in matched)
    unclosed = tuple(
        span.name
        for span in opens
        if span not in matched_opens and span.name not in duplicate_names
    )
    duplicate_blocks = tuple(dict.fromkeys(name for name in open_names if name in duplicate_names))
    expected_set = set(expected)
    found_set = set(found)
    missing = tuple(b for b in expected if b not in found_set)
    extra = tuple(name for name in found if name not in expected_set)

    found_in_expected = []
    seen_found_in_expected: set[str] = set()
    for name in found:
        if name in expected_set and name not in seen_found_in_expected:
            found_in_expected.append(name)
            seen_found_in_expected.add(name)
    expected_present = [b for b in expected if b in seen_found_in_expected]
    out_of_order: tuple[str, ...] = ()
    if found_in_expected != expected_present:
        out_of_order = tuple(
            actual
            for actual, want in zip(found_in_expected, expected_present, strict=True)
            if actual != want
        )

    if not opens:
        level = ComplianceLevel.NONE
    elif missing or extra or out_of_order or duplicate_blocks or unclosed:
        level = ComplianceLevel.PARTIAL
    else:
        level = ComplianceLevel.FULL

    return ValidationResult(
        level=level,
        found_blocks=found,
        missing_blocks=missing,
        extra_blocks=extra,
        out_of_order=out_of_order,
        duplicate_blocks=duplicate_blocks,
        unclosed_blocks=unclosed,
        data_warnings=tuple(data_warnings),
    )
