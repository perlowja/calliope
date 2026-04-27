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

"""JobOutcome + RenderReport — driver output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JobOutcome:
    """Per-job result.

    `success=True` means the renderable's `render()` and any file write
    completed without raising an `Exception`. Drivers capture
    `Exception` subclasses into failed outcomes; `BaseException`
    subclasses propagate intentionally. `html_output` is set when the
    job had no `output_path`; otherwise it is `None`.
    """

    name: str
    success: bool
    duration_ms: float
    output_path: Path | None = None
    html_output: str | None = None
    error: str | None = None
    error_type: str | None = None

    def __post_init__(self) -> None:
        if self.duration_ms < 0:
            raise ValueError("JobOutcome.duration_ms must be >= 0")
        if self.success and self.error:
            raise ValueError("JobOutcome cannot have success=True and a non-empty error")


@dataclass(frozen=True)
class RenderReport:
    """Aggregate driver report."""

    __hash__ = None

    outcomes: tuple[JobOutcome, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.outcomes, tuple):
            raise TypeError("RenderReport.outcomes must be a tuple")
        for outcome in self.outcomes:
            if not isinstance(outcome, JobOutcome):
                raise TypeError(
                    f"RenderReport.outcomes entries must be JobOutcome, "
                    f"got {type(outcome).__name__}"
                )

    @property
    def total_jobs(self) -> int:
        return len(self.outcomes)

    @property
    def success_count(self) -> int:
        return sum(1 for o in self.outcomes if o.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for o in self.outcomes if not o.success)

    @property
    def total_duration_ms(self) -> float:
        return sum(o.duration_ms for o in self.outcomes)

    @property
    def is_clean(self) -> bool:
        return self.failure_count == 0

    def failures(self) -> tuple[JobOutcome, ...]:
        return tuple(o for o in self.outcomes if not o.success)
