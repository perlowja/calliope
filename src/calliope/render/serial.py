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

"""SerialRenderDriver — one job at a time, in input order.

The reference driver. Use this in tests, in single-page renders, or
when deterministic ordering matters.
"""

from __future__ import annotations

from collections.abc import Iterable

from calliope.render._runner import execute_job, prepare_jobs
from calliope.render.job import RenderJob
from calliope.render.report import RenderReport


class SerialRenderDriver:
    """Run jobs sequentially in submission order."""

    def run(self, jobs: Iterable[RenderJob]) -> RenderReport:
        job_list = prepare_jobs(jobs)
        outcomes = tuple(execute_job(job) for job in job_list)
        return RenderReport(outcomes=outcomes)
