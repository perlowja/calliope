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

from calliope.assets import Asset, AssetManifest, manifest_from_assets


def test_empty_manifest_is_valid():
    m = AssetManifest()
    assert len(m) == 0
    assert m.published("anything") is None


def test_manifest_published_returns_value():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    assert m.published("main.css") == "main.abcd.css"


def test_manifest_published_returns_none_for_unknown():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    assert m.published("missing.css") is None


def test_manifest_contains():
    m = AssetManifest(entries={"main.css": "main.abcd.css"})
    assert "main.css" in m
    assert "missing.css" not in m
    assert 42 not in m  # type: ignore[operator]


def test_manifest_iter_yields_logical_paths():
    m = AssetManifest(entries={"a.css": "a.x.css", "b.js": "b.y.js"})
    assert set(m) == {"a.css", "b.js"}


def test_manifest_entries_become_readonly_proxy():
    m = AssetManifest(entries={"a.css": "a.x.css"})
    assert isinstance(m.entries, MappingProxyType)
    with pytest.raises(TypeError):
        m.entries["a.css"] = "tampered"  # type: ignore[index]


def test_manifest_defensively_copies_entries():
    src = {"a.css": "a.x.css"}
    m = AssetManifest(entries=src)
    src["a.css"] = "MUTATED"
    src["b.css"] = "ADDED"
    assert m.published("a.css") == "a.x.css"
    assert "b.css" not in m


def test_manifest_rejects_non_str_key():
    with pytest.raises(TypeError):
        AssetManifest(entries={42: "x"})  # type: ignore[dict-item]


def test_manifest_rejects_non_str_value():
    with pytest.raises(TypeError):
        AssetManifest(entries={"a.css": 42})  # type: ignore[dict-item]


def test_manifest_is_unhashable():
    m = AssetManifest(entries={"a.css": "a.x.css"})
    with pytest.raises(TypeError):
        hash(m)


def test_manifest_from_assets_builds_correctly():
    a1 = Asset(logical_path="a.css", content=b"x", content_hash="aaaa1111")
    a2 = Asset(logical_path="b.js", content=b"y", content_hash="bbbb2222")
    m = manifest_from_assets([a1, a2])
    assert m.published("a.css") == "a.aaaa1111.css"
    assert m.published("b.js") == "b.bbbb2222.js"


def test_manifest_from_assets_rejects_duplicate_logical_paths():
    a1 = Asset(logical_path="a.css", content=b"x", content_hash="aaaa1111")
    a2 = Asset(logical_path="a.css", content=b"y", content_hash="bbbb2222")
    with pytest.raises(ValueError, match="duplicate logical_path"):
        manifest_from_assets([a1, a2])
