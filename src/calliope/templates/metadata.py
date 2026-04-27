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

"""Template metadata — the page-shell contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class TemplateMetadata:
    """Immutable page-shell contract.

    `blocks` is ordered: validation checks sequence, not just membership.
    `fallbacks` is a read-only mapping backed by a defensive copy.
    """

    __hash__ = None

    template_name: str
    version: str
    blocks: tuple[str, ...]
    required_fields: tuple[str, ...] = ()
    optional_fields: tuple[str, ...] = ()
    fallbacks: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.template_name:
            raise ValueError("template_name must be non-empty")
        if not self.version:
            raise ValueError("version must be non-empty")
        if not isinstance(self.blocks, tuple):
            raise TypeError("blocks must be a tuple (immutable, ordered)")
        if len(set(self.blocks)) != len(self.blocks):
            raise ValueError(f"blocks must be unique: {self.blocks!r}")
        if not isinstance(self.required_fields, tuple):
            raise TypeError("required_fields must be a tuple")
        if not isinstance(self.optional_fields, tuple):
            raise TypeError("optional_fields must be a tuple")
        if not isinstance(self.fallbacks, Mapping):
            raise TypeError("fallbacks must be a Mapping")
        object.__setattr__(self, "fallbacks", MappingProxyType(dict(self.fallbacks)))

    def fallback_for(self, key: str, default: Any = "") -> Any:
        return self.fallbacks.get(key, default)
