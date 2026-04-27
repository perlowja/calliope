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

"""ThreadedRenderDriver — parallel via `concurrent.futures.ThreadPoolExecutor`.

Threads sidestep pickling, so adapters can pass renderables that close
over Jinja2 environments, file handles, or other unpicklable state.
For CPU-bound HTML rendering, threads do not give CPython parallelism
(GIL-bound); they are useful when rendering is I/O-bound (waits on
database queries, asset hashing, etc.).

Adapters that need real CPU parallelism should write a process-pool
driver in their own layer; calliope does not ship one because Jinja
environments and adapter callbacks are typically not picklable.
"""

from __future__ import annotations

from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

from calliope.render._runner import execute_job, prepare_jobs
from calliope.render.job import RenderJob
from calliope.render.report import RenderReport


class ThreadedRenderDriver:
    """Run jobs in a `ThreadPoolExecutor`; outcomes are returned in input order."""

    def __init__(self, *, max_workers: int | None = None) -> None:
        if max_workers is not None and max_workers < 1:
            raise ValueError("max_workers must be >= 1 or None")
        self._max_workers = max_workers

    @property
    def max_workers(self) -> int | None:
        return self._max_workers

    def run(self, jobs: Iterable[RenderJob]) -> RenderReport:
        job_list = prepare_jobs(jobs)
        if not job_list:
            return RenderReport(outcomes=())
        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            outcomes = tuple(pool.map(execute_job, job_list))
        return RenderReport(outcomes=outcomes)
