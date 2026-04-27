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

"""Taxonomy — domain key → display tuple lookup.

Subsumes the cleanroom pattern of repeated `LICENSE_TYPE_MAP`,
`INSPECTION_TYPE_MAP`, `DISPOSITION_MAP`, `ENTITY_TYPE_MAP` dicts. Each
of those is a `key → (label, css_class, color)` mapping with a fallback
entry for unknowns; calliope ships the abstraction, adapters supply the
concrete entries.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True)
class TaxonomyEntry:
    """Display attributes for a taxonomy member."""

    label: str
    css_class: str = ""
    color: str | None = None


_DEFAULT_FALLBACK = TaxonomyEntry(label="Unknown", css_class="taxonomy-unknown")


@dataclass(frozen=True)
class Taxonomy:
    """Immutable key → `TaxonomyEntry` mapping with explicit fallback.

    `entries` is a `Mapping[str, TaxonomyEntry]` — adapters typically pass
    a plain dict; non-string keys are rejected and the dataclass
    defensively copies into a frozen `MappingProxyType`.
    """

    __hash__ = None

    name: str
    entries: Mapping[str, TaxonomyEntry] = field(default_factory=dict)
    fallback: TaxonomyEntry = _DEFAULT_FALLBACK

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Taxonomy.name must be non-empty")
        if not isinstance(self.entries, Mapping):
            raise TypeError("Taxonomy.entries must be a Mapping")
        for key, value in self.entries.items():
            if not isinstance(key, str):
                raise TypeError(f"Taxonomy.entries keys must be str, got {type(key).__name__}")
            if not isinstance(value, TaxonomyEntry):
                raise TypeError(
                    f"Taxonomy.entries[{key!r}] must be a TaxonomyEntry, got {type(value).__name__}"
                )
        if not isinstance(self.fallback, TaxonomyEntry):
            raise TypeError("Taxonomy.fallback must be a TaxonomyEntry")
        object.__setattr__(self, "entries", MappingProxyType(dict(self.entries)))

    def get(self, key: str | None) -> TaxonomyEntry:
        if key is None:
            return self.fallback
        return self.entries.get(key, self.fallback)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self.entries

    def __len__(self) -> int:
        return len(self.entries)
