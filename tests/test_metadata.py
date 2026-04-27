# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from calliope.templates import TemplateMetadata


def _meta(**overrides) -> TemplateMetadata:
    base = dict(
        template_name="page.dimension",
        version="1.0.0",
        blocks=("header", "nav", "content", "footer"),
    )
    base.update(overrides)
    return TemplateMetadata(**base)


def test_minimal_metadata_constructs():
    m = _meta()
    assert m.template_name == "page.dimension"
    assert m.version == "1.0.0"
    assert m.blocks == ("header", "nav", "content", "footer")


def test_metadata_is_frozen():
    m = _meta()
    with pytest.raises(FrozenInstanceError):
        m.template_name = "other"


def test_blocks_must_be_tuple():
    with pytest.raises(TypeError):
        _meta(blocks=["header", "footer"])


def test_blocks_must_be_unique():
    with pytest.raises(ValueError):
        _meta(blocks=("header", "header"))


def test_template_name_required():
    with pytest.raises(ValueError):
        _meta(template_name="")


def test_version_required():
    with pytest.raises(ValueError):
        _meta(version="")


def test_fallbacks_become_readonly_mapping():
    m = _meta(fallbacks={"foo": "bar"})
    assert isinstance(m.fallbacks, MappingProxyType)
    assert m.fallbacks["foo"] == "bar"
    with pytest.raises(TypeError):
        m.fallbacks["foo"] = "baz"  # type: ignore[index]


def test_fallbacks_are_defensively_copied_from_mapping_proxy():
    source = {"foo": "bar"}
    m = _meta(fallbacks=MappingProxyType(source))
    source["foo"] = "baz"
    source["new"] = "value"
    assert dict(m.fallbacks) == {"foo": "bar"}


def test_metadata_is_explicitly_unhashable():
    with pytest.raises(TypeError):
        hash(_meta())


def test_fallback_for_returns_default_when_missing():
    m = _meta(fallbacks={"foo": "bar"})
    assert m.fallback_for("foo") == "bar"
    assert m.fallback_for("missing") == ""
    assert m.fallback_for("missing", default="X") == "X"


def test_default_fallbacks_is_empty_mapping():
    m = _meta()
    assert dict(m.fallbacks) == {}
