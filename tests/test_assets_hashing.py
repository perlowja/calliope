# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.assets import (
    DEFAULT_HASH_LENGTH,
    MAX_HASH_LENGTH,
    MIN_HASH_LENGTH,
    hash_content,
)


def test_hash_default_length():
    assert len(hash_content(b"hello")) == DEFAULT_HASH_LENGTH


def test_hash_is_lowercase_hex():
    h = hash_content(b"hello")
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_is_deterministic():
    assert hash_content(b"hello") == hash_content(b"hello")


def test_hash_changes_when_content_changes():
    assert hash_content(b"hello") != hash_content(b"world")


def test_hash_length_min_and_max_accepted():
    assert len(hash_content(b"x", length=MIN_HASH_LENGTH)) == MIN_HASH_LENGTH
    assert len(hash_content(b"x", length=MAX_HASH_LENGTH)) == MAX_HASH_LENGTH


def test_hash_rejects_too_short_length():
    with pytest.raises(ValueError):
        hash_content(b"x", length=MIN_HASH_LENGTH - 1)


def test_hash_rejects_too_long_length():
    with pytest.raises(ValueError):
        hash_content(b"x", length=MAX_HASH_LENGTH + 1)


def test_hash_rejects_non_int_length():
    with pytest.raises(TypeError):
        hash_content(b"x", length=10.0)  # type: ignore[arg-type]


def test_hash_rejects_bool_length():
    with pytest.raises(TypeError):
        hash_content(b"x", length=True)  # type: ignore[arg-type]


def test_hash_rejects_non_bytes_data():
    with pytest.raises(TypeError):
        hash_content("hello")  # type: ignore[arg-type]


def test_hash_accepts_bytearray_and_memoryview():
    expected = hash_content(b"hello")
    assert hash_content(bytearray(b"hello")) == expected
    assert hash_content(memoryview(b"hello")) == expected
