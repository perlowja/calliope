# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from calliope.cards import CardRenderer
from calliope.templates import TemplateMetadata


class _StructuralCard:
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(template_name="card.demo", version="1.0.0", blocks=("body",))

    def render(self, row: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> str:
        return f"<div>{row.get('title', '')}</div>"


class _NotACard:
    def render(self, row: Mapping[str, Any]) -> str:
        return ""


def test_structural_match_satisfies_protocol():
    assert isinstance(_StructuralCard(), CardRenderer)


def test_missing_metadata_does_not_satisfy_protocol():
    assert not isinstance(_NotACard(), CardRenderer)
