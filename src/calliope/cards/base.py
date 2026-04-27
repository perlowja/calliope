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

"""CardTemplate ABC + JinjaCardTemplate concrete base.

Mirrors `calliope.templates.PageTemplate` and `JinjaPageTemplate` but
with per-row semantics. CardTemplate satisfies `CardRenderer` Protocol
structurally.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from calliope.templates import TemplateMetadata, bind_data

if TYPE_CHECKING:
    from jinja2 import Environment


class CardTemplate(ABC):
    """Abstract per-row card renderer.

    Concrete subclasses provide `metadata` and `render`. `render` accepts
    any `Mapping[str, Any]` row and must not mutate it.
    """

    @property
    @abstractmethod
    def metadata(self) -> TemplateMetadata: ...

    @abstractmethod
    def render(
        self,
        row: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...

    @property
    def expected_blocks(self) -> tuple[str, ...]:
        return self.metadata.blocks

    @property
    def required_fields(self) -> tuple[str, ...]:
        return self.metadata.required_fields


class JinjaCardTemplate(CardTemplate):
    """Concrete `CardTemplate` backed by a Jinja2 environment.

    Subclasses set `jinja_template_name` and provide `metadata`. Override
    `bind_context()` to shape the per-row mapping before rendering.
    """

    jinja_template_name: str = ""

    def __init__(self, environment: Environment) -> None:
        if not self.jinja_template_name:
            raise ValueError(
                f"{type(self).__name__} must set class attribute `jinja_template_name`"
            )
        self._env = environment

    def bind_context(
        self,
        row: Mapping[str, Any],
        context: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        bound, warnings = bind_data(self.metadata, row, strict=False)
        merged = dict(context or {})
        merged.update(bound)
        merged.setdefault("_warnings", warnings)
        return merged

    def render(
        self,
        row: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str:
        template = self._env.get_template(self.jinja_template_name)
        return template.render(self.bind_context(row, context))
