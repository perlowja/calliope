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

"""Dependency-injected template registry.

There is no global singleton. Adapters or test fixtures construct a
`TemplateRegistry`, register templates, and inject it where needed.

Multi-version coexistence is supported by the data model but not required
at Stage 1. When two versions of the same template are registered,
`get(name)` selects the highest version using `packaging.version.Version`.
"""

from __future__ import annotations

from collections.abc import Iterable

from packaging.version import Version

from calliope.templates.base import PageTemplate


class TemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], PageTemplate] = {}

    def register(self, template: PageTemplate, *, replace: bool = False) -> None:
        meta = template.metadata
        Version(meta.version)
        key = (meta.template_name, meta.version)
        if key in self._templates and not replace:
            raise ValueError(
                f"template already registered: {meta.template_name!r}@{meta.version!r}"
            )
        self._templates[key] = template

    def get(self, template_name: str, version: str | None = None) -> PageTemplate:
        if version is not None:
            try:
                return self._templates[(template_name, version)]
            except KeyError:
                raise KeyError(f"template not found: {template_name!r}@{version!r}") from None

        candidates = [(name, ver) for (name, ver) in self._templates if name == template_name]
        if not candidates:
            raise KeyError(f"template not found: {template_name!r}")

        latest = max(candidates, key=lambda nv: Version(nv[1]))
        return self._templates[latest]

    def list_templates(self) -> tuple[str, ...]:
        return tuple(sorted({name for name, _ in self._templates}))

    def list_versions(self, template_name: str) -> tuple[str, ...]:
        versions = [ver for (name, ver) in self._templates if name == template_name]
        versions.sort(key=Version)
        return tuple(versions)

    def __len__(self) -> int:
        return len(self._templates)

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            return any(name == key for name, _ in self._templates)
        if isinstance(key, tuple) and len(key) == 2:
            return key in self._templates
        return False

    def __iter__(self) -> Iterable[tuple[str, str]]:
        return iter(self._templates)
