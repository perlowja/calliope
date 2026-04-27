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

"""Tier — score-to-label classification with optional emoji.

The cleanroom `get_tier(score)` returned hardcoded RiskyEats tiers:
EXCELLENT / GOOD / CAUTION / HIGH RISK / CRITICAL. Calliope makes this
caller-supplied: a `TierTable` is an ordered tuple of `Tier` objects,
each with a `min_score` threshold. `classify(score)` returns the
highest-threshold tier whose threshold is `<= score`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    name: str
    label: str
    min_score: float = 0.0
    emoji: str | None = None
    css_class: str = ""
    color: str | None = None


@dataclass(frozen=True)
class TierTable:
    """Ordered tier classification table.

    Tiers are stored in ascending `min_score` order with duplicate
    thresholds rejected. `classify(score)` returns the tier with the
    highest `min_score` not exceeding `score`, or the lowest tier if
    `score` is below every threshold.
    """

    __hash__ = None

    name: str
    tiers: tuple[Tier, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("TierTable.name must be non-empty")
        if not self.tiers:
            raise ValueError("TierTable.tiers must be non-empty")
        if not isinstance(self.tiers, tuple):
            raise TypeError("TierTable.tiers must be a tuple")
        sorted_tiers = tuple(sorted(self.tiers, key=lambda t: t.min_score))
        for previous, current in zip(sorted_tiers, sorted_tiers[1:], strict=False):
            if previous.min_score == current.min_score:
                raise ValueError("TierTable.tiers must have unique min_score values")
        if sorted_tiers != self.tiers:
            object.__setattr__(self, "tiers", sorted_tiers)

    def classify(self, score: float) -> Tier:
        chosen = self.tiers[0]
        for tier in self.tiers:
            if score >= tier.min_score:
                chosen = tier
            else:
                break
        return chosen


def make_tier_table(name: str, tiers: Iterable[Tier]) -> TierTable:
    """Convenience constructor that accepts any iterable."""
    return TierTable(name=name, tiers=tuple(tiers))
