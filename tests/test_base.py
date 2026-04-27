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

from calliope.templates import (
    JinjaPageTemplate,
    PageTemplate,
    TemplateMetadata,
    bind_data,
    safe_value,
)

# ---------- safe_value ----------


def test_safe_value_none_returns_empty():
    assert safe_value(None) == ""


def test_safe_value_int_thousands_separator():
    assert safe_value(1234567) == "1,234,567"


def test_safe_value_float_two_decimals():
    assert safe_value(3.14159) == "3.14"


def test_safe_value_bool():
    assert safe_value(True) == "Yes"
    assert safe_value(False) == "No"


def test_safe_value_escapes_html_by_default():
    assert safe_value("<script>") == "&lt;script&gt;"


def test_safe_value_can_skip_escape():
    assert safe_value("<b>", escape_html=False) == "<b>"


def test_safe_value_list_joins_and_escapes_per_item():
    assert safe_value(["<a>", "b"]) == "&lt;a&gt;, b"


# ---------- bind_data ----------


def _meta(**kw):
    base = dict(
        template_name="page.test",
        version="1.0.0",
        blocks=("header",),
        required_fields=("title",),
        optional_fields=("description",),
        fallbacks={"description": "default desc"},
    )
    base.update(kw)
    return TemplateMetadata(**base)


def test_bind_data_strict_raises_on_missing_required():
    m = _meta()
    with pytest.raises(ValueError):
        bind_data(m, {})


def test_bind_data_strict_raises_when_required_is_none():
    m = _meta()
    with pytest.raises(ValueError):
        bind_data(m, {"title": None})


def test_bind_data_lenient_uses_fallback_for_missing_required():
    m = _meta(fallbacks={"title": "FALLBACK", "description": "default desc"})
    bound, warnings = bind_data(m, {}, strict=False)
    assert bound["title"] == "FALLBACK"
    assert any("title" in w for w in warnings)


def test_bind_data_preserves_undeclared_keys():
    m = _meta()
    bound, warnings = bind_data(m, {"title": "T", "css_path": "/a.css", "site_title": "S"})
    assert bound["css_path"] == "/a.css"
    assert bound["site_title"] == "S"
    assert warnings == ()


def test_bind_data_applies_optional_fallback_when_missing():
    m = _meta()
    bound, _ = bind_data(m, {"title": "T"})
    assert bound["description"] == "default desc"


def test_bind_data_does_not_overwrite_provided_optional():
    m = _meta()
    bound, _ = bind_data(m, {"title": "T", "description": "explicit"})
    assert bound["description"] == "explicit"


def test_bind_data_does_not_mutate_input():
    m = _meta()
    src: dict[str, Any] = {"title": "T"}
    bind_data(m, src)
    assert src == {"title": "T"}


# ---------- PageTemplate ABC ----------


def test_page_template_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        PageTemplate()  # type: ignore[abstract]


class _Concrete(PageTemplate):
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            template_name="page.t",
            version="1",
            blocks=("a",),
        )

    def render(self, data: Mapping[str, Any], context=None) -> str:
        return f"<!-- BLOCK:a -->{safe_value(data.get('x'))}<!-- /BLOCK:a -->"


def test_concrete_subclass_renders():
    t = _Concrete()
    out = t.render({"x": 42})
    assert "42" in out
    assert t.expected_blocks == ("a",)


# ---------- JinjaPageTemplate ----------


class _MyJinjaPage(JinjaPageTemplate):
    jinja_template_name = "page.html.j2"

    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            template_name="page.jinja",
            version="1.0.0",
            blocks=("header",),
            required_fields=("title",),
        )


def _env() -> Environment:
    return Environment(
        loader=DictLoader(
            {"page.html.j2": ("<!-- BLOCK:header -->{{ title }}<!-- /BLOCK:header -->")}
        ),
        autoescape=True,
    )


def test_jinja_page_template_renders():
    t = _MyJinjaPage(_env())
    out = t.render({"title": "Hi"})
    assert "<!-- BLOCK:header -->Hi<!-- /BLOCK:header -->" in out


def test_jinja_page_template_requires_jinja_template_name():
    class Broken(JinjaPageTemplate):
        @property
        def metadata(self) -> TemplateMetadata:
            return TemplateMetadata("page.broken", "1", ("a",))

    with pytest.raises(ValueError):
        Broken(_env())


def test_jinja_page_template_does_not_mutate_data():
    t = _MyJinjaPage(_env())
    src = {"title": "Hi"}
    t.render(src)
    assert src == {"title": "Hi"}
