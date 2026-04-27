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

"""RenderJob — a unit of render work.

Adapters construct a `RenderJob` for each page (or card) they want to
emit. Drivers consume an iterable of jobs and return a `RenderReport`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from calliope.render.protocol import Renderable


@dataclass(frozen=True)
class RenderJob:
    """A single render unit.

    `name` is for logging and reporting (typically a route or page id).
    `output_path` is optional: if set, the driver writes the rendered HTML
    there; if None, the driver returns the HTML in the outcome and writes
    nothing.
    """

    __hash__ = None

    name: str
    renderable: Renderable
    data: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] | None = None
    output_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("RenderJob.name must be non-empty")
        if not isinstance(self.data, Mapping):
            raise TypeError("RenderJob.data must be a Mapping")
        if self.context is not None and not isinstance(self.context, Mapping):
            raise TypeError("RenderJob.context must be a Mapping or None")
        if self.output_path is not None and not isinstance(self.output_path, Path):
            raise TypeError("RenderJob.output_path must be a pathlib.Path or None")
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))
        if self.context is not None:
            object.__setattr__(self, "context", MappingProxyType(dict(self.context)))
