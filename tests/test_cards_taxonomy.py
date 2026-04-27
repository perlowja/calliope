# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from types import MappingProxyType

import pytest

from calliope.cards import Taxonomy, TaxonomyEntry


def test_taxonomy_get_returns_entry_for_known_key():
    t = Taxonomy(
        name="license_type",
        entries={"2010": TaxonomyEntry(label="Restaurant", css_class="pill-rest")},
    )
    e = t.get("2010")
    assert e.label == "Restaurant"
    assert e.css_class == "pill-rest"


def test_taxonomy_get_returns_fallback_for_unknown_key():
    t = Taxonomy(
        name="license_type",
        entries={"2010": TaxonomyEntry(label="Restaurant")},
        fallback=TaxonomyEntry(label="Other", css_class="pill-other"),
    )
    assert t.get("9999").label == "Other"


def test_taxonomy_get_returns_fallback_for_none():
    t = Taxonomy(name="x", entries={"a": TaxonomyEntry(label="A")})
    assert t.get(None).label == "Unknown"


def test_taxonomy_rejects_non_string_key_at_construction():
    with pytest.raises(TypeError, match="Taxonomy.entries keys must be str"):
        Taxonomy(
            name="x",
            entries={42: TaxonomyEntry(label="forty-two")},
        )  # type: ignore[dict-item]


def test_taxonomy_entries_are_defensively_copied():
    src = {"a": TaxonomyEntry(label="A")}
    t = Taxonomy(name="x", entries=src)
    src["a"] = TaxonomyEntry(label="MUTATED")
    src["b"] = TaxonomyEntry(label="ADDED")
    assert t.get("a").label == "A"
    assert t.get("b").label == "Unknown"


def test_taxonomy_rejects_non_mapping_entries():
    with pytest.raises(TypeError):
        Taxonomy(name="x", entries=[("a", TaxonomyEntry(label="A"))])  # type: ignore[arg-type]


def test_taxonomy_rejects_non_taxonomy_entry_value():
    with pytest.raises(TypeError):
        Taxonomy(name="x", entries={"a": ("wrong", "shape")})  # type: ignore[dict-item]


def test_taxonomy_requires_non_empty_name():
    with pytest.raises(ValueError):
        Taxonomy(name="")


def test_taxonomy_is_unhashable():
    t = Taxonomy(name="x", entries={"a": TaxonomyEntry(label="A")})
    with pytest.raises(TypeError):
        hash(t)


def test_taxonomy_entries_become_readonly_proxy():
    t = Taxonomy(name="x", entries={"a": TaxonomyEntry(label="A")})
    assert isinstance(t.entries, MappingProxyType)
    with pytest.raises(TypeError):
        t.entries["a"] = TaxonomyEntry(label="changed")  # type: ignore[index]


def test_taxonomy_contains_and_len():
    t = Taxonomy(name="x", entries={"a": TaxonomyEntry(label="A")})
    assert "a" in t
    assert "b" not in t
    assert 1 not in t  # type: ignore[arg-type]
    assert len(t) == 1
