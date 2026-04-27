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

"""Render-stage Protocols.

`Renderable` covers anything that produces HTML from a per-page or per-row
mapping; both `templates.PageTemplate` and `cards.CardRenderer` satisfy it
structurally. `RenderDriver` is the Protocol render drivers implement.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from calliope.render.job import RenderJob
    from calliope.render.report import RenderReport
    from calliope.templates import TemplateMetadata


@runtime_checkable
class Renderable(Protocol):
    """Anything with `metadata` and `render` matching the calliope shape.

    `PageTemplate`, `JinjaPageTemplate`, `CardTemplate`, `JinjaCardTemplate`,
    and any structurally-matching adapter class all satisfy this Protocol.
    """

    @property
    def metadata(self) -> TemplateMetadata: ...

    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...


@runtime_checkable
class RenderDriver(Protocol):
    """Executes a batch of `RenderJob`s and returns a `RenderReport`."""

    def run(self, jobs: Iterable[RenderJob]) -> RenderReport: ...
