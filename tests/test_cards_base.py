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

import pytest
from jinja2 import DictLoader, Environment

from calliope.cards import CardRenderer, CardTemplate, JinjaCardTemplate
from calliope.templates import TemplateMetadata


class _Concrete(CardTemplate):
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            template_name="card.demo",
            version="1.0.0",
            blocks=("body",),
            required_fields=("title",),
        )

    def render(self, row: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> str:
        return f"<!-- BLOCK:body -->{row.get('title', '')}<!-- /BLOCK:body -->"


def test_card_template_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        CardTemplate()  # type: ignore[abstract]


def test_card_template_satisfies_card_renderer_protocol():
    assert isinstance(_Concrete(), CardRenderer)


def test_card_template_exposes_metadata_helpers():
    t = _Concrete()
    assert t.expected_blocks == ("body",)
    assert t.required_fields == ("title",)


class _MyJinjaCard(JinjaCardTemplate):
    jinja_template_name = "card.html.j2"

    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            template_name="card.jinja",
            version="1.0.0",
            blocks=("body",),
            required_fields=("title",),
        )


def _env() -> Environment:
    return Environment(
        loader=DictLoader({"card.html.j2": "<!-- BLOCK:body -->{{ title }}<!-- /BLOCK:body -->"}),
        autoescape=True,
    )


def test_jinja_card_template_renders_per_row():
    t = _MyJinjaCard(_env())
    out = t.render({"title": "row-A"})
    assert "<!-- BLOCK:body -->row-A<!-- /BLOCK:body -->" in out


def test_jinja_card_template_requires_jinja_template_name():
    class Broken(JinjaCardTemplate):
        @property
        def metadata(self) -> TemplateMetadata:
            return TemplateMetadata("card.broken", "1.0.0", ("a",))

    with pytest.raises(ValueError):
        Broken(_env())


def test_jinja_card_template_does_not_mutate_row():
    t = _MyJinjaCard(_env())
    src = {"title": "T"}
    t.render(src)
    assert src == {"title": "T"}
