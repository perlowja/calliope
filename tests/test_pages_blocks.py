# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from calliope.pages import (
    DETAIL_PAGE_BLOCKS,
    DIMENSION_PAGE_BLOCKS,
    INDEX_PAGE_BLOCKS,
    LIST_PAGE_BLOCKS,
)


def test_block_tuples_are_tuples():
    for tup in (INDEX_PAGE_BLOCKS, LIST_PAGE_BLOCKS, DIMENSION_PAGE_BLOCKS, DETAIL_PAGE_BLOCKS):
        assert isinstance(tup, tuple)


def test_block_tuples_are_unique():
    for tup in (INDEX_PAGE_BLOCKS, LIST_PAGE_BLOCKS, DIMENSION_PAGE_BLOCKS, DETAIL_PAGE_BLOCKS):
        assert len(set(tup)) == len(tup), f"duplicates in {tup!r}"


def test_block_names_are_kebab_case():
    import re

    pattern = re.compile(r"^[a-z][a-z0-9-]*$")
    for tup in (INDEX_PAGE_BLOCKS, LIST_PAGE_BLOCKS, DIMENSION_PAGE_BLOCKS, DETAIL_PAGE_BLOCKS):
        for name in tup:
            assert pattern.match(name), f"non-kebab-case: {name!r}"


def test_dimension_page_blocks_match_production_sequence():
    """Documented to match L1_metagenerator.py:1331-1369 production output."""
    assert DIMENSION_PAGE_BLOCKS == (
        "head",
        "header",
        "nav",
        "how-to-use",
        "stats",
        "signup",
        "news",
        "content",
        "legal",
        "footer",
    )


def test_index_page_blocks_start_with_head_header_nav():
    assert INDEX_PAGE_BLOCKS[:3] == ("head", "header", "nav")


def test_list_page_blocks_include_pagination():
    assert "pagination" in LIST_PAGE_BLOCKS


def test_block_tuples_can_be_used_as_metadata_blocks():
    from calliope.templates import TemplateMetadata

    for name, tup in (
        ("page.index", INDEX_PAGE_BLOCKS),
        ("page.list", LIST_PAGE_BLOCKS),
        ("page.dimension", DIMENSION_PAGE_BLOCKS),
        ("page.detail", DETAIL_PAGE_BLOCKS),
    ):
        meta = TemplateMetadata(template_name=name, version="1.0.0", blocks=tup)
        assert meta.blocks == tup
