# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

"""Pagination primitives.

The cleanroom rendered paginated lists by computing slice offsets inline
in each generator. Calliope ships an `Iterator`-based `paginate()` and
a frozen `PaginationPage` so adapters can stream large result sets
without eagerly materializing every page.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Pagination:
    """Page-position metadata.

    `page_number` is 1-based to match human-readable URLs and template
    expectations (`page-1.html`, `page-2.html`).
    """

    page_number: int
    total_pages: int
    items_per_page: int
    total_items: int

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError("page_number must be >= 1")
        if self.total_pages < 1:
            raise ValueError("total_pages must be >= 1")
        if self.items_per_page < 1:
            raise ValueError("items_per_page must be >= 1")
        if self.total_items < 0:
            raise ValueError("total_items must be >= 0")
        expected_total_pages = max(
            1, (self.total_items + self.items_per_page - 1) // self.items_per_page
        )
        if self.total_pages != expected_total_pages:
            raise ValueError(
                f"total_pages {self.total_pages} does not match total_items/items_per_page "
                f"expectation {expected_total_pages}"
            )
        if self.page_number > self.total_pages:
            raise ValueError(
                f"page_number {self.page_number} exceeds total_pages {self.total_pages}"
            )

    @property
    def is_first(self) -> bool:
        return self.page_number == 1

    @property
    def is_last(self) -> bool:
        return self.page_number == self.total_pages

    @property
    def has_previous(self) -> bool:
        return not self.is_first

    @property
    def has_next(self) -> bool:
        return not self.is_last

    @property
    def previous_page(self) -> int | None:
        return self.page_number - 1 if self.has_previous else None

    @property
    def next_page(self) -> int | None:
        return self.page_number + 1 if self.has_next else None


@dataclass(frozen=True)
class PaginationPage:
    """A single rendered page slice.

    `items` is a tuple to keep the dataclass frozen and hashable up to
    the item type's own hashability.
    """

    pagination: Pagination
    items: tuple[T, ...]


def paginate(items: Sequence[T], items_per_page: int) -> Iterator[PaginationPage]:
    """Stream `items` as a sequence of `PaginationPage` slices.

    Always emits at least one page, even if `items` is empty (an empty
    site index page is still a valid page). `items_per_page` must be
    `>= 1`.
    """
    if items_per_page < 1:
        raise ValueError("items_per_page must be >= 1")

    total_items = len(items)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

    for page_number in range(1, total_pages + 1):
        start = (page_number - 1) * items_per_page
        end = start + items_per_page
        slice_ = tuple(items[start:end])
        yield PaginationPage(
            pagination=Pagination(
                page_number=page_number,
                total_pages=total_pages,
                items_per_page=items_per_page,
                total_items=total_items,
            ),
            items=slice_,
        )
