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

"""Internal helper — execute one `RenderJob` and produce its `JobOutcome`.

Shared by `SerialRenderDriver` and `ThreadedRenderDriver`. Centralizes the
render-write-time-error contract so both drivers report consistently.
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Iterable
from contextlib import suppress

from calliope.render.job import RenderJob
from calliope.render.report import JobOutcome


def _duration_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0


def _failed_outcome(job: RenderJob, started: float, exc: Exception) -> JobOutcome:
    return JobOutcome(
        name=job.name,
        success=False,
        duration_ms=_duration_ms(started),
        output_path=job.output_path,
        html_output=None,
        error=str(exc),
        error_type=type(exc).__name__,
    )


def prepare_jobs(jobs: Iterable[RenderJob]) -> tuple[RenderJob, ...]:
    """Materialize a batch and reject duplicate output paths before rendering."""
    job_list = tuple(jobs)
    seen_paths: set[object] = set()
    for job in job_list:
        if job.output_path is None:
            continue
        if job.output_path in seen_paths:
            raise ValueError(f"duplicate output_path in batch: {job.output_path}")
        seen_paths.add(job.output_path)
    return job_list


def _write_html_atomically(path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + f".tmp.{uuid.uuid4().hex}")
    try:
        tmp_path.write_text(html, encoding="utf-8")
        os.replace(tmp_path, path)
    except Exception:
        with suppress(OSError):
            tmp_path.unlink()
        raise


def execute_job(job: RenderJob) -> JobOutcome:
    """Run a single job; capture `Exception`, allow `BaseException` to propagate."""
    started = time.perf_counter()
    try:
        html = job.renderable.render(job.data, job.context)
    except Exception as exc:  # noqa: BLE001 -- driver contract intentionally catches all
        return _failed_outcome(job, started, exc)

    if job.output_path is not None:
        try:
            _write_html_atomically(job.output_path, html)
        except Exception as exc:  # noqa: BLE001 -- driver contract intentionally catches all
            return _failed_outcome(job, started, exc)
        return JobOutcome(
            name=job.name,
            success=True,
            duration_ms=_duration_ms(started),
            output_path=job.output_path,
            html_output=None,
        )

    return JobOutcome(
        name=job.name,
        success=True,
        duration_ms=_duration_ms(started),
        output_path=None,
        html_output=html,
    )
