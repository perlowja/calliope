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

"""Narrative — convert numeric or categorical signals into prose.

The cleanroom L1_narrative.py converts violation counts into
DBPR-specific prose. Calliope ships a Protocol and a Jinja-backed
default; adapters supply the actual phrasing templates.

Two implementations:

- `NarrativeRenderer` Protocol — structural contract.
- `TemplateNarrativeRenderer` — concrete renderer that delegates to a
  Jinja2 template named at construction.

Adapters that need AI-generated narrative implement the Protocol with
their own renderer (calliope does not ship an AI client).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from jinja2 import Environment


@runtime_checkable
class NarrativeRenderer(Protocol):
    def render(self, signals: Mapping[str, Any]) -> str: ...


class TemplateNarrativeRenderer:
    """Render narrative prose by passing signals to a Jinja2 template.

    The `template_name` is a Jinja loader key. The rendered output is
    returned verbatim with leading/trailing whitespace stripped — Jinja
    templates often add stray newlines at the boundary.
    """

    def __init__(self, environment: Environment, template_name: str) -> None:
        if not template_name:
            raise ValueError("template_name must be non-empty")
        self._env = environment
        self._template_name = template_name

    @property
    def template_name(self) -> str:
        return self._template_name

    def render(self, signals: Mapping[str, Any]) -> str:
        template = self._env.get_template(self._template_name)
        return template.render(dict(signals)).strip()
