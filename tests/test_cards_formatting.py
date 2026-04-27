# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from datetime import date, datetime

import pytest

from calliope.cards import format_iso_date, slugify


def test_format_iso_date_from_datetime():
    assert format_iso_date(datetime(2026, 4, 27, 13, 45)) == "2026-04-27"


def test_format_iso_date_from_date():
    assert format_iso_date(date(2026, 4, 27)) == "2026-04-27"


def test_format_iso_date_from_iso_string_truncates_to_ten():
    assert format_iso_date("2026-04-27T13:45:00Z") == "2026-04-27"


def test_format_iso_date_handles_none():
    assert format_iso_date(None) == ""
    assert format_iso_date(None, default="N/A") == "N/A"


def test_format_iso_date_handles_empty_string():
    assert format_iso_date("") == ""


def test_format_iso_date_handles_short_string():
    assert format_iso_date("2026-04") == "2026-04"


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_strips_diacritics():
    assert slugify("Crème brûlée") == "creme-brulee"


def test_slugify_collapses_punctuation():
    assert slugify("Mom's Diner & Co.!!!") == "mom-s-diner-co"


def test_slugify_empty_input():
    assert slugify("") == ""


def test_slugify_only_punctuation():
    assert slugify("!!!") == ""


def test_slugify_idempotent():
    once = slugify("Mom's Diner")
    twice = slugify(once)
    assert once == twice


def test_slugify_custom_separator():
    assert slugify("hello world", separator="_") == "hello_world"


def test_slugify_custom_separator_strips_edges():
    assert slugify(" hello ", separator="_") == "hello"


def test_slugify_max_length_truncates_and_strips_trailing_separator():
    # Truncation that lands on a separator boundary strips the trailing dash.
    assert slugify("abc def ghi", max_length=8) == "abc-def"


def test_slugify_idempotent_with_multichar_separator_and_truncation():
    once = slugify("abc def", separator="--", max_length=4)
    twice = slugify(once, separator="--", max_length=4)
    assert twice == once


def test_slugify_truncation_strips_partial_separator_remnant():
    assert slugify("abc def", separator="--", max_length=4) == "abc"


@pytest.mark.parametrize("text", ["abc def ghi"])
@pytest.mark.parametrize("separator", ["-", "_", "--"])
@pytest.mark.parametrize("max_length", [None, 4, 8, 12])
def test_slugify_idempotent_across_separator_and_truncation_matrix(
    text: str, separator: str, max_length: int | None
):
    once = slugify(text, separator=separator, max_length=max_length)
    twice = slugify(once, separator=separator, max_length=max_length)
    assert twice == once


def test_slugify_rejects_negative_max_length():
    with pytest.raises(ValueError, match="max_length"):
        slugify("hello", max_length=-1)


def test_slugify_max_length_within_word():
    out = slugify("alphabet soup", max_length=10)
    assert out == "alphabet-s"  # exact 10 chars; no trailing dash to strip


def test_slugify_lowercases_uppercase():
    assert slugify("AAAA") == "aaaa"
