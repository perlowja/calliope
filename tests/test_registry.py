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
from packaging.version import InvalidVersion

from calliope.templates import (
    PageTemplate,
    TemplateMetadata,
    TemplateRegistry,
)


class _Stub(PageTemplate):
    def __init__(self, name: str, version: str) -> None:
        self._meta = TemplateMetadata(template_name=name, version=version, blocks=("a",))

    @property
    def metadata(self) -> TemplateMetadata:
        return self._meta

    def render(self, data: Mapping[str, Any], context=None) -> str:
        return ""


def test_registry_register_and_get_exact_version():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.0.0"))
    r.register(_Stub("page.demo", "1.1.0"))
    t = r.get("page.demo", "1.0.0")
    assert t.metadata.version == "1.0.0"


def test_registry_get_returns_latest_by_pep440():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.0.0"))
    r.register(_Stub("page.demo", "1.10.0"))
    r.register(_Stub("page.demo", "1.2.0"))
    t = r.get("page.demo")
    assert t.metadata.version == "1.10.0"  # not "1.2.0" via lexicographic


def test_registry_raises_keyerror_for_unknown_template():
    r = TemplateRegistry()
    with pytest.raises(KeyError):
        r.get("page.missing")


def test_registry_raises_keyerror_for_unknown_version():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.0.0"))
    with pytest.raises(KeyError):
        r.get("page.demo", "9.9.9")


def test_registry_list_templates_returns_unique_sorted():
    r = TemplateRegistry()
    r.register(_Stub("page.b", "1.0.0"))
    r.register(_Stub("page.a", "1.0.0"))
    r.register(_Stub("page.a", "1.1.0"))
    assert r.list_templates() == ("page.a", "page.b")


def test_registry_list_versions_orders_by_pep440():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.10.0"))
    r.register(_Stub("page.demo", "1.2.0"))
    assert r.list_versions("page.demo") == ("1.2.0", "1.10.0")


def test_registry_register_rejects_invalid_versions():
    r = TemplateRegistry()
    with pytest.raises(InvalidVersion):
        r.register(_Stub("page.demo", "not-a-version"))


def test_registry_register_rejects_duplicate_name_version_without_replace():
    r = TemplateRegistry()
    original = _Stub("page.demo", "1.0.0")
    replacement = _Stub("page.demo", "1.0.0")
    r.register(original)
    with pytest.raises(ValueError, match="already registered"):
        r.register(replacement)
    assert r.get("page.demo", "1.0.0") is original


def test_registry_register_replace_overwrites_existing_template():
    r = TemplateRegistry()
    original = _Stub("page.demo", "1.0.0")
    replacement = _Stub("page.demo", "1.0.0")
    r.register(original)
    r.register(replacement, replace=True)
    assert r.get("page.demo", "1.0.0") is replacement


def test_registry_contains_by_name():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.0.0"))
    assert "page.demo" in r
    assert "page.absent" not in r


def test_registry_contains_by_pair():
    r = TemplateRegistry()
    r.register(_Stub("page.demo", "1.0.0"))
    assert ("page.demo", "1.0.0") in r
    assert ("page.demo", "9.9.9") not in r


def test_registry_is_isolated_per_instance():
    r1 = TemplateRegistry()
    r2 = TemplateRegistry()
    r1.register(_Stub("page.demo", "1.0.0"))
    assert "page.demo" in r1
    assert "page.demo" not in r2
    assert len(r2) == 0
