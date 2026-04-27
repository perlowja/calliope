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

"""Page-shell contracts: metadata, validation, extraction, registry, helpers.

See ``docs/CALLIOPE-SPEC.md`` for the architectural shape.
"""

from calliope.templates.base import (
    JinjaPageTemplate,
    PageTemplate,
    bind_data,
    safe_value,
)
from calliope.templates.extraction import extract_blocks
from calliope.templates.metadata import TemplateMetadata
from calliope.templates.registry import TemplateRegistry
from calliope.templates.validation import (
    CLOSE_RE,
    OPEN_RE,
    ComplianceLevel,
    ValidationResult,
    detect_blocks,
    validate_output,
)

__all__ = [
    "CLOSE_RE",
    "ComplianceLevel",
    "JinjaPageTemplate",
    "OPEN_RE",
    "PageTemplate",
    "TemplateMetadata",
    "TemplateRegistry",
    "ValidationResult",
    "bind_data",
    "detect_blocks",
    "extract_blocks",
    "safe_value",
    "validate_output",
]
