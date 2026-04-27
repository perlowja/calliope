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

"""RenderResult — produced by render drivers, not by templates.

The AEDIFEX reference coupled `RenderResult` to its `StaticSiteGenerator`,
which mixed bind / render / validate / extract / write into one object.
Calliope keeps the data shape but moves it to `calliope.render` so render
drivers can produce results without the `templates/` layer importing
render-stage concerns.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from calliope.templates.validation import ValidationResult


@dataclass(frozen=True)
class RenderResult:
    template_name: str
    template_version: str
    html_output: str
    blocks: Mapping[str, str]
    validation: ValidationResult
    render_time_ms: float
