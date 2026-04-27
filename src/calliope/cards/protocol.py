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

"""CardRenderer Protocol — the swappable contract for per-row card renderers.

Adapters can pick a renderer by name from a manifest at site-build time.
The Protocol intentionally does not require subclassing, only a structural
match: a class with `metadata` and `render` is a `CardRenderer`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from calliope.templates import TemplateMetadata


@runtime_checkable
class CardRenderer(Protocol):
    """Renders a single row's card HTML.

    Per-row semantics: `render()` is called once per data row with that
    row's mapping. Site-level aggregates (counts, navigation) belong in
    `calliope.pages`, not here.
    """

    @property
    def metadata(self) -> TemplateMetadata: ...

    def render(
        self,
        row: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...
