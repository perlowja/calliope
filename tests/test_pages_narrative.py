# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest
from jinja2 import DictLoader, Environment

from calliope.pages import NarrativeRenderer, TemplateNarrativeRenderer


def _env(template_body: str) -> Environment:
    return Environment(loader=DictLoader({"narrative.j2": template_body}))


class _StructuralRenderer:
    def render(self, signals):
        return f"prose with {signals.get('count', 0)}"


def test_protocol_satisfied_by_structural_class():
    assert isinstance(_StructuralRenderer(), NarrativeRenderer)


def test_template_renderer_satisfies_protocol():
    r = TemplateNarrativeRenderer(_env("{{ count }}"), "narrative.j2")
    assert isinstance(r, NarrativeRenderer)


def test_template_renderer_renders_signals():
    r = TemplateNarrativeRenderer(_env("Found {{ count }} items"), "narrative.j2")
    assert r.render({"count": 7}) == "Found 7 items"


def test_template_renderer_strips_boundary_whitespace():
    r = TemplateNarrativeRenderer(_env("\n\n  hello  \n\n"), "narrative.j2")
    assert r.render({}) == "hello"


def test_template_renderer_rejects_empty_template_name():
    with pytest.raises(ValueError):
        TemplateNarrativeRenderer(_env("{{ x }}"), "")


def test_template_renderer_does_not_mutate_signals():
    r = TemplateNarrativeRenderer(_env("{{ x }}"), "narrative.j2")
    src = {"x": 1}
    r.render(src)
    assert src == {"x": 1}


def test_template_renderer_exposes_template_name():
    r = TemplateNarrativeRenderer(_env("{{ x }}"), "narrative.j2")
    assert r.template_name == "narrative.j2"


def test_protocol_advisory_check_does_not_validate_callability():
    class FakeRenderer:
        render = "not a callable"

    # runtime_checkable Protocols only check attribute presence, not type.
    assert isinstance(FakeRenderer(), NarrativeRenderer)
