# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.cards import Tier, TierTable, make_tier_table


def _five_tier_table() -> TierTable:
    return TierTable(
        name="risk",
        tiers=(
            Tier(name="excellent", label="EXCELLENT", min_score=0.0, emoji="✅"),
            Tier(name="good", label="GOOD", min_score=20.0, emoji="🟢"),
            Tier(name="caution", label="CAUTION", min_score=40.0, emoji="🟡"),
            Tier(name="high", label="HIGH RISK", min_score=60.0, emoji="🟠"),
            Tier(name="critical", label="CRITICAL", min_score=80.0, emoji="🔴"),
        ),
    )


def test_classify_below_first_threshold_returns_lowest():
    t = _five_tier_table()
    assert t.classify(-10).name == "excellent"
    assert t.classify(0).name == "excellent"


def test_classify_returns_correct_tier_at_threshold():
    t = _five_tier_table()
    assert t.classify(20).name == "good"
    assert t.classify(40).name == "caution"
    assert t.classify(60).name == "high"
    assert t.classify(80).name == "critical"


def test_classify_returns_highest_when_above_top():
    t = _five_tier_table()
    assert t.classify(1000).name == "critical"


def test_tier_table_sorts_unsorted_input():
    t = TierTable(
        name="x",
        tiers=(
            Tier(name="b", label="B", min_score=10),
            Tier(name="a", label="A", min_score=0),
        ),
    )
    assert [tier.name for tier in t.tiers] == ["a", "b"]


def test_tier_table_rejects_empty():
    with pytest.raises(ValueError):
        TierTable(name="x", tiers=())


def test_tier_table_rejects_duplicate_min_scores():
    with pytest.raises(ValueError, match="unique min_score"):
        TierTable(
            name="x",
            tiers=(
                Tier(name="a", label="A", min_score=0),
                Tier(name="b", label="B", min_score=0),
            ),
        )


def test_tier_table_rejects_non_tuple():
    with pytest.raises(TypeError):
        TierTable(name="x", tiers=[Tier(name="a", label="A")])  # type: ignore[arg-type]


def test_tier_table_requires_name():
    with pytest.raises(ValueError):
        TierTable(name="", tiers=(Tier(name="a", label="A"),))


def test_tier_table_is_unhashable():
    t = _five_tier_table()
    with pytest.raises(TypeError):
        hash(t)


def test_make_tier_table_accepts_iterable():
    t = make_tier_table(
        "x",
        iter([Tier(name="a", label="A", min_score=0), Tier(name="b", label="B", min_score=5)]),
    )
    assert isinstance(t, TierTable)
    assert t.classify(7).name == "b"
