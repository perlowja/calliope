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

"""PageTemplate ABC, safe_value, bind_data, JinjaPageTemplate.

`bind_data` operates on a single mapping per page. List-of-pages is the
render driver's concern, not the template's.
"""

from __future__ import annotations

import html as _html
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from calliope.templates.metadata import TemplateMetadata

if TYPE_CHECKING:
    from jinja2 import Environment


def safe_value(value: Any, *, escape_html: bool = True) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, (list, tuple)):
        text = ", ".join(safe_value(v, escape_html=False) for v in value)
    else:
        text = str(value)
    return _html.escape(text) if escape_html else text


def bind_data(
    metadata: TemplateMetadata,
    data: Mapping[str, Any],
    *,
    strict: bool = True,
) -> tuple[Mapping[str, Any], tuple[str, ...]]:
    """Bind a single page's data against `metadata`.

    Returns `(bound, warnings)`. In strict mode, missing required fields
    raise `ValueError`. In lenient mode, missing required fields fall back
    to `metadata.fallbacks` and emit a warning.

    Unlike the AEDIFEX reference, undeclared keys in `data` are preserved.
    The metadata is the page-shell contract for required/optional fields,
    not an exhaustive whitelist.
    """
    bound: dict[str, Any] = dict(data)
    warnings: list[str] = []

    for key in metadata.required_fields:
        if data.get(key) is None:
            if strict:
                raise ValueError(f"missing required field: {key!r}")
            bound[key] = metadata.fallback_for(key)
            warnings.append(f"missing required field {key!r}, using fallback")

    for key in metadata.optional_fields:
        if bound.get(key) is None:
            fallback = metadata.fallback_for(key, default=None)
            if fallback is not None:
                bound[key] = fallback

    return bound, tuple(warnings)


class PageTemplate(ABC):
    """Abstract page-shell template.

    Concrete subclasses provide `metadata` and `render`. Calliope ships
    `JinjaPageTemplate` as the recommended base for HTML pages.
    """

    @property
    @abstractmethod
    def metadata(self) -> TemplateMetadata: ...

    @abstractmethod
    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...

    @property
    def expected_blocks(self) -> tuple[str, ...]:
        return self.metadata.blocks

    @property
    def required_fields(self) -> tuple[str, ...]:
        return self.metadata.required_fields


class JinjaPageTemplate(PageTemplate):
    """Concrete `PageTemplate` backed by a Jinja2 environment.

    Subclasses set `jinja_template_name` and provide `metadata`. Override
    `bind_context()` to shape per-page data before rendering. Subclasses
    must not mutate `data`.
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
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        bound, warnings = bind_data(self.metadata, data, strict=False)
        merged = dict(context or {})
        merged.update(bound)
        merged.setdefault("_warnings", warnings)
        return merged

    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str:
        template = self._env.get_template(self.jinja_template_name)
        return template.render(self.bind_context(data, context))
