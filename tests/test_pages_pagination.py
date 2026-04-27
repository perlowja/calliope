# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.pages import Pagination, PaginationPage, paginate


def test_pagination_constructs_single_page():
    p = Pagination(page_number=1, total_pages=1, items_per_page=10, total_items=3)
    assert p.is_first
    assert p.is_last
    assert not p.has_previous
    assert not p.has_next
    assert p.previous_page is None
    assert p.next_page is None


def test_pagination_constructs_middle_page():
    p = Pagination(page_number=2, total_pages=4, items_per_page=10, total_items=35)
    assert not p.is_first
    assert not p.is_last
    assert p.has_previous
    assert p.has_next
    assert p.previous_page == 1
    assert p.next_page == 3


def test_pagination_rejects_zero_page_number():
    with pytest.raises(ValueError, match="page_number"):
        Pagination(page_number=0, total_pages=1, items_per_page=10, total_items=0)


def test_pagination_rejects_page_beyond_total():
    with pytest.raises(ValueError, match="exceeds"):
        Pagination(page_number=5, total_pages=4, items_per_page=10, total_items=35)


def test_pagination_rejects_zero_items_per_page():
    with pytest.raises(ValueError, match="items_per_page"):
        Pagination(page_number=1, total_pages=1, items_per_page=0, total_items=0)


def test_pagination_rejects_negative_total_items():
    with pytest.raises(ValueError, match="total_items"):
        Pagination(page_number=1, total_pages=1, items_per_page=10, total_items=-1)


def test_pagination_rejects_inconsistent_total_pages():
    with pytest.raises(ValueError, match="total_pages"):
        Pagination(page_number=1, total_pages=1, items_per_page=10, total_items=999)


def test_paginate_emits_one_page_for_empty_input():
    pages = list(paginate([], items_per_page=10))
    assert len(pages) == 1
    assert pages[0].items == ()
    assert pages[0].pagination.total_pages == 1
    assert pages[0].pagination.total_items == 0


def test_paginate_splits_evenly_divisible():
    pages = list(paginate(list(range(20)), items_per_page=5))
    assert len(pages) == 4
    assert pages[0].items == (0, 1, 2, 3, 4)
    assert pages[3].items == (15, 16, 17, 18, 19)
    for i, page in enumerate(pages, start=1):
        assert page.pagination.page_number == i
        assert page.pagination.total_pages == 4


def test_paginate_handles_remainder():
    pages = list(paginate(list(range(7)), items_per_page=3))
    assert len(pages) == 3
    assert pages[2].items == (6,)


def test_paginate_rejects_zero_items_per_page():
    with pytest.raises(ValueError):
        list(paginate([1, 2], items_per_page=0))


def test_pagination_page_items_are_tuple():
    pages = list(paginate([1, 2, 3], items_per_page=5))
    assert isinstance(pages[0], PaginationPage)
    assert isinstance(pages[0].items, tuple)
