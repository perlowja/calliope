# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from calliope.assets import Asset


def test_asset_published_path_inserts_hash_before_extension():
    a = Asset(logical_path="main.css", content=b"x", content_hash="a1b2c3d4")
    assert a.published_path == "main.a1b2c3d4.css"


def test_asset_published_path_in_subdirectory():
    a = Asset(logical_path="css/main.css", content=b"x", content_hash="abcd1234")
    assert a.published_path == "css/main.abcd1234.css"


def test_asset_published_path_handles_no_extension():
    a = Asset(logical_path="LICENSE", content=b"x", content_hash="abcd1234")
    assert a.published_path == "LICENSE.abcd1234"


def test_asset_published_path_handles_dot_in_directory():
    a = Asset(logical_path="some.dir/file.js", content=b"x", content_hash="aaaa1111")
    assert a.published_path == "some.dir/file.aaaa1111.js"


def test_asset_size_returns_byte_length():
    assert Asset(logical_path="x.css", content=b"hello", content_hash="abcd1234").size == 5


def test_asset_rejects_empty_logical_path():
    with pytest.raises(ValueError):
        Asset(logical_path="", content=b"x", content_hash="abcd1234")


def test_asset_rejects_absolute_logical_path():
    with pytest.raises(ValueError):
        Asset(logical_path="/main.css", content=b"x", content_hash="abcd1234")


def test_asset_rejects_non_bytes_content():
    with pytest.raises(TypeError):
        Asset(logical_path="x.css", content="hello", content_hash="abcd1234")  # type: ignore[arg-type]


def test_asset_accepts_bytearray_and_normalizes_to_bytes():
    a = Asset(logical_path="x.css", content=bytearray(b"hi"), content_hash="abcd1234")
    assert isinstance(a.content, bytes)


def test_asset_rejects_empty_hash():
    with pytest.raises(ValueError):
        Asset(logical_path="x.css", content=b"x", content_hash="")


def test_asset_rejects_non_hex_hash():
    with pytest.raises(ValueError):
        Asset(logical_path="x.css", content=b"x", content_hash="GHIJKL")


def test_asset_is_frozen():
    a = Asset(logical_path="x.css", content=b"x", content_hash="abcd1234")
    with pytest.raises(FrozenInstanceError):
        a.logical_path = "other.css"  # type: ignore[misc]
