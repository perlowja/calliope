# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import math

import pytest

from calliope.cards import HeatbarSegment, render_heatbar


def test_render_heatbar_zero_fill_returns_empty():
    out = render_heatbar(
        [HeatbarSegment(weight=1.0)],
        fill_pct=0,
    )
    assert out == ""


def test_render_heatbar_negative_fill_returns_empty():
    out = render_heatbar(
        [HeatbarSegment(weight=1.0)],
        fill_pct=-50,
    )
    assert out == ""


def test_render_heatbar_no_positive_segments_returns_empty():
    out = render_heatbar(
        [HeatbarSegment(weight=0), HeatbarSegment(weight=-1)],
        fill_pct=50,
    )
    assert out == ""


def test_render_heatbar_clamps_fill_pct_to_100():
    out = render_heatbar(
        [HeatbarSegment(weight=1)],
        fill_pct=150,
    )
    assert "100.0%" in out


def test_render_heatbar_segments_split_proportionally():
    out = render_heatbar(
        [
            HeatbarSegment(weight=1, css_class="severe", color="#dc2626"),
            HeatbarSegment(weight=3, css_class="basic", color="#10b981"),
        ],
        fill_pct=80,
    )
    assert 'class="heatbar"' in out
    assert "width:20.0%" in out
    assert "width:60.0%" in out
    assert "background:#dc2626;" in out
    assert "background:#10b981;" in out


def test_render_heatbar_skips_zero_weight_segments():
    out = render_heatbar(
        [
            HeatbarSegment(weight=0, css_class="absent"),
            HeatbarSegment(weight=1, css_class="present"),
        ],
        fill_pct=50,
    )
    assert "absent" not in out
    assert "present" in out


@pytest.mark.parametrize("weight", [math.inf, -math.inf, math.nan])
def test_render_heatbar_skips_non_finite_segments(weight: float):
    out = render_heatbar(
        [
            HeatbarSegment(weight=weight, css_class="invalid"),
            HeatbarSegment(weight=1, css_class="valid"),
        ],
        fill_pct=50,
    )
    assert "invalid" not in out
    assert "valid" in out
    assert "width:50.0%" in out


def test_render_heatbar_emits_container_title():
    out = render_heatbar(
        [HeatbarSegment(weight=1)],
        fill_pct=50,
        title="Score: 50",
    )
    assert 'title="Score: 50"' in out


def test_render_heatbar_segment_title():
    out = render_heatbar(
        [HeatbarSegment(weight=1, title="HP=3")],
        fill_pct=50,
    )
    assert 'title="HP=3"' in out
