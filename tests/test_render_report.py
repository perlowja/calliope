# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import pytest

from calliope.render import JobOutcome, RenderReport


def _ok(name: str, ms: float = 1.0, html: str = "<div>") -> JobOutcome:
    return JobOutcome(name=name, success=True, duration_ms=ms, html_output=html)


def _fail(name: str, ms: float = 1.0, err: str = "boom") -> JobOutcome:
    return JobOutcome(
        name=name,
        success=False,
        duration_ms=ms,
        error=err,
        error_type="RuntimeError",
    )


def test_outcome_rejects_negative_duration():
    with pytest.raises(ValueError, match="duration"):
        JobOutcome(name="n", success=True, duration_ms=-1.0)


def test_outcome_rejects_success_with_error():
    with pytest.raises(ValueError, match="success"):
        JobOutcome(name="n", success=True, duration_ms=1.0, error="oh no")


def test_report_aggregates_counts_and_duration():
    r = RenderReport(
        outcomes=(_ok("a", ms=10), _ok("b", ms=20), _fail("c", ms=30)),
    )
    assert r.total_jobs == 3
    assert r.success_count == 2
    assert r.failure_count == 1
    assert r.total_duration_ms == 60.0
    assert not r.is_clean


def test_report_is_clean_when_all_succeed():
    r = RenderReport(outcomes=(_ok("a"), _ok("b")))
    assert r.is_clean


def test_report_failures_returns_only_failed_outcomes():
    r = RenderReport(outcomes=(_ok("a"), _fail("b"), _ok("c"), _fail("d")))
    assert tuple(o.name for o in r.failures()) == ("b", "d")


def test_report_rejects_non_tuple_outcomes():
    with pytest.raises(TypeError):
        RenderReport(outcomes=[_ok("a")])  # type: ignore[arg-type]


def test_report_rejects_non_outcome_entries():
    with pytest.raises(TypeError):
        RenderReport(outcomes=("not an outcome",))  # type: ignore[arg-type]


def test_report_is_unhashable():
    r = RenderReport(outcomes=())
    with pytest.raises(TypeError):
        hash(r)


def test_empty_report_metrics():
    r = RenderReport(outcomes=())
    assert r.total_jobs == 0
    assert r.success_count == 0
    assert r.failure_count == 0
    assert r.total_duration_ms == 0.0
    assert r.is_clean
