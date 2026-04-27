# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from calliope.render import (
    Renderable,
    RenderDriver,
    RenderJob,
    RenderReport,
)
from calliope.templates import TemplateMetadata


class _MinimalRenderable:
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(template_name="page.t", version="1.0.0", blocks=("body",))

    def render(self, data: Mapping[str, Any], context=None) -> str:
        return "<div></div>"


class _MinimalDriver:
    def run(self, jobs: Iterable[RenderJob]) -> RenderReport:
        return RenderReport(outcomes=())


def test_renderable_protocol_satisfied_structurally():
    assert isinstance(_MinimalRenderable(), Renderable)


def test_render_driver_protocol_satisfied_structurally():
    assert isinstance(_MinimalDriver(), RenderDriver)


def test_page_template_satisfies_renderable_via_metadata_and_render():
    from calliope.templates import PageTemplate

    class P(PageTemplate):
        @property
        def metadata(self) -> TemplateMetadata:
            return TemplateMetadata("page.x", "1.0.0", ("body",))

        def render(self, data, context=None):
            return ""

    assert isinstance(P(), Renderable)


def test_card_template_satisfies_renderable():
    from calliope.cards import CardTemplate

    class C(CardTemplate):
        @property
        def metadata(self) -> TemplateMetadata:
            return TemplateMetadata("card.x", "1.0.0", ("body",))

        def render(self, row, context=None):
            return ""

    assert isinstance(C(), Renderable)


def test_object_without_render_does_not_satisfy_renderable():
    class NoRender:
        @property
        def metadata(self):
            return TemplateMetadata("x.y", "1", ("a",))

    assert not isinstance(NoRender(), Renderable)


def test_run_method_attribute_required_for_render_driver():
    class NoRun:
        pass

    assert not isinstance(NoRun(), RenderDriver)
