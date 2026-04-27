# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

from calliope.render import RenderJob
from calliope.templates import TemplateMetadata


class _Stub:
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata("page.s", "1.0.0", ("body",))

    def render(self, data: Mapping[str, Any], context=None) -> str:
        return ""


def test_minimal_job_constructs_with_defaults():
    j = RenderJob(name="page-1", renderable=_Stub())
    assert j.name == "page-1"
    assert isinstance(j.data, Mapping)
    assert dict(j.data) == {}
    assert j.context is None
    assert j.output_path is None


def test_job_data_is_defensively_copied():
    src = {"x": 1}
    j = RenderJob(name="n", renderable=_Stub(), data=src)
    src["x"] = 999
    src["y"] = 2
    assert dict(j.data) == {"x": 1}


def test_job_data_becomes_readonly_proxy():
    j = RenderJob(name="n", renderable=_Stub(), data={"a": 1})
    assert isinstance(j.data, MappingProxyType)
    with pytest.raises(TypeError):
        j.data["a"] = 2  # type: ignore[index]


def test_job_context_is_defensively_copied():
    src = {"k": "v"}
    j = RenderJob(name="n", renderable=_Stub(), context=src)
    src["k"] = "MUTATED"
    assert dict(j.context) == {"k": "v"}  # type: ignore[arg-type]


def test_job_rejects_empty_name():
    with pytest.raises(ValueError, match="name"):
        RenderJob(name="", renderable=_Stub())


def test_job_rejects_non_mapping_data():
    with pytest.raises(TypeError, match="data"):
        RenderJob(name="n", renderable=_Stub(), data=[("a", 1)])  # type: ignore[arg-type]


def test_job_rejects_non_path_output_path():
    with pytest.raises(TypeError, match="output_path"):
        RenderJob(name="n", renderable=_Stub(), output_path="/tmp/x.html")  # type: ignore[arg-type]


def test_job_accepts_path_output_path():
    j = RenderJob(name="n", renderable=_Stub(), output_path=Path("/tmp/x.html"))
    assert j.output_path == Path("/tmp/x.html")


def test_job_is_unhashable_due_to_mapping_fields():
    j = RenderJob(name="n", renderable=_Stub())
    with pytest.raises(TypeError):
        hash(j)
