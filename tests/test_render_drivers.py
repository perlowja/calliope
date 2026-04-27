# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

import calliope.render._runner as render_runner
from calliope.render import (
    RenderJob,
    SerialRenderDriver,
    ThreadedRenderDriver,
)
from calliope.templates import TemplateMetadata


class _ConstRenderer:
    def __init__(self, body: str) -> None:
        self._body = body

    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata("page.const", "1.0.0", ("body",))

    def render(self, data: Mapping[str, Any], context=None) -> str:
        return self._body


class _BoomRenderer:
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata("page.boom", "1.0.0", ("body",))

    def render(self, data: Mapping[str, Any], context=None) -> str:
        raise RuntimeError("boom")


class _CountingRenderer:
    def __init__(self, body: str) -> None:
        self._body = body
        self.calls = 0

    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata("page.counting", "1.0.0", ("body",))

    def render(self, data: Mapping[str, Any], context=None) -> str:
        self.calls += 1
        return self._body


# --- shared driver behavior tests, parametrized over driver class ---


@pytest.fixture(params=[SerialRenderDriver, ThreadedRenderDriver])
def driver(request):
    return request.param()


def test_driver_runs_jobs_and_returns_html_when_no_output_path(driver):
    jobs = [
        RenderJob(name="a", renderable=_ConstRenderer("<a/>")),
        RenderJob(name="b", renderable=_ConstRenderer("<b/>")),
    ]
    report = driver.run(jobs)
    assert report.total_jobs == 2
    assert report.is_clean
    by_name = {o.name: o for o in report.outcomes}
    assert by_name["a"].html_output == "<a/>"
    assert by_name["b"].html_output == "<b/>"
    assert by_name["a"].output_path is None


def test_driver_writes_output_path_and_creates_parent_dirs(driver, tmp_path):
    out = tmp_path / "deep" / "nested" / "page.html"
    job = RenderJob(name="page", renderable=_ConstRenderer("<x/>"), output_path=out)
    report = driver.run([job])
    assert report.is_clean
    assert out.exists()
    assert out.read_text(encoding="utf-8") == "<x/>"
    outcome = report.outcomes[0]
    assert outcome.output_path == out
    assert outcome.html_output is None


def test_driver_captures_render_exception_as_failed_outcome(driver):
    jobs = [
        RenderJob(name="ok", renderable=_ConstRenderer("<ok/>")),
        RenderJob(name="bad", renderable=_BoomRenderer()),
    ]
    report = driver.run(jobs)
    assert report.total_jobs == 2
    assert report.success_count == 1
    assert report.failure_count == 1
    bad = next(o for o in report.outcomes if o.name == "bad")
    assert not bad.success
    assert bad.error == "boom"
    assert bad.error_type == "RuntimeError"
    assert bad.html_output is None


def test_driver_durations_are_non_negative(driver):
    jobs = [RenderJob(name=f"p{i}", renderable=_ConstRenderer("<x/>")) for i in range(3)]
    report = driver.run(jobs)
    for outcome in report.outcomes:
        assert outcome.duration_ms >= 0
    assert report.total_duration_ms >= 0


def test_driver_empty_jobs_returns_empty_clean_report(driver):
    report = driver.run([])
    assert report.total_jobs == 0
    assert report.is_clean


def test_driver_run_does_not_mutate_input_iterable(driver):
    jobs = [RenderJob(name="x", renderable=_ConstRenderer("<x/>"))]
    driver.run(iter(jobs))  # exhaust the iterator
    # jobs list is unchanged
    assert len(jobs) == 1


def test_driver_rejects_duplicate_output_paths_before_render(driver, tmp_path):
    renderer = _CountingRenderer("<x/>")
    output_path = tmp_path / "shared.html"
    jobs = [
        RenderJob(name="a", renderable=renderer, output_path=output_path),
        RenderJob(name="b", renderable=renderer, output_path=output_path),
    ]

    with pytest.raises(ValueError, match="duplicate output_path in batch") as excinfo:
        driver.run(jobs)

    assert str(output_path) in str(excinfo.value)
    assert renderer.calls == 0


def test_driver_captures_unicode_encode_error(driver, tmp_path):
    output_path = tmp_path / "page.html"
    job = RenderJob(name="bad-write", renderable=_ConstRenderer("\ud800"), output_path=output_path)

    report = driver.run([job])

    assert report.failure_count == 1
    outcome = report.outcomes[0]
    assert not outcome.success
    assert outcome.error_type == "UnicodeEncodeError"
    assert not output_path.exists()
    assert not tuple(tmp_path.glob("page.html.tmp.*"))


def test_driver_captures_arbitrary_exception_during_write(driver, tmp_path, monkeypatch):
    def raise_lookup_error(
        self, data: str, encoding: str | None = None, errors: str | None = None, newline=None
    ) -> int:
        raise LookupError("unknown encoding")

    monkeypatch.setattr(Path, "write_text", raise_lookup_error)
    output_path = tmp_path / "page.html"
    job = RenderJob(name="bad-write", renderable=_ConstRenderer("<x/>"), output_path=output_path)

    report = driver.run([job])

    assert report.failure_count == 1
    outcome = report.outcomes[0]
    assert not outcome.success
    assert outcome.error_type == "LookupError"
    assert outcome.error == "unknown encoding"
    assert not output_path.exists()


def test_driver_atomic_write_replaces_existing_file(driver, tmp_path):
    output_path = tmp_path / "page.html"

    first = driver.run(
        [RenderJob(name="page-v1", renderable=_ConstRenderer("<v1/>"), output_path=output_path)]
    )
    second = driver.run(
        [RenderJob(name="page-v2", renderable=_ConstRenderer("<v2/>"), output_path=output_path)]
    )

    assert first.is_clean
    assert second.is_clean
    assert output_path.read_text(encoding="utf-8") == "<v2/>"
    assert not tuple(tmp_path.glob("page.html.tmp.*"))


def test_driver_failed_write_does_not_leave_temp_files(driver, tmp_path, monkeypatch):
    def raise_replace(src, dst) -> None:
        raise RuntimeError("replace failed")

    monkeypatch.setattr(render_runner.os, "replace", raise_replace)
    output_path = tmp_path / "page.html"
    job = RenderJob(name="bad-write", renderable=_ConstRenderer("<x/>"), output_path=output_path)

    report = driver.run([job])

    assert report.failure_count == 1
    outcome = report.outcomes[0]
    assert not outcome.success
    assert outcome.error_type == "RuntimeError"
    assert not tuple(tmp_path.glob("page.html.tmp.*"))


# --- driver-specific tests ---


def test_serial_driver_preserves_input_order():
    driver = SerialRenderDriver()
    names = [f"page-{i:03d}" for i in range(20)]
    jobs = [RenderJob(name=n, renderable=_ConstRenderer(f"<{n}/>")) for n in names]
    report = driver.run(jobs)
    assert tuple(o.name for o in report.outcomes) == tuple(names)


def test_threaded_driver_preserves_input_order():
    driver = ThreadedRenderDriver(max_workers=4)
    names = [f"page-{i:03d}" for i in range(20)]
    jobs = [RenderJob(name=n, renderable=_ConstRenderer(f"<{n}/>")) for n in names]
    report = driver.run(jobs)
    # ThreadedRenderDriver promises input-order outcomes (via pool.map).
    assert tuple(o.name for o in report.outcomes) == tuple(names)


def test_threaded_driver_rejects_zero_workers():
    with pytest.raises(ValueError):
        ThreadedRenderDriver(max_workers=0)


def test_threaded_driver_rejects_negative_workers():
    with pytest.raises(ValueError):
        ThreadedRenderDriver(max_workers=-1)


def test_threaded_driver_default_max_workers_is_none():
    assert ThreadedRenderDriver().max_workers is None


def test_driver_oserror_during_write_is_captured(driver, tmp_path):
    # Make the parent directory unwritable: a file with the parent's name
    # exists, so creating the parent dir fails.
    blocker = tmp_path / "page.html"
    blocker.write_text("blocker")
    # Now request writing INTO that file as a directory -> fails.
    output_path = blocker / "child.html"
    job = RenderJob(name="bad-write", renderable=_ConstRenderer("<x/>"), output_path=output_path)
    report = driver.run([job])
    assert report.failure_count == 1
    outcome = report.outcomes[0]
    assert outcome.error_type in {"FileExistsError", "NotADirectoryError"}
