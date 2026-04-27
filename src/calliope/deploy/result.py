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

"""DeployResult — outcome returned by `DeployTarget.deploy()`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeployResult:
    target_name: str
    success: bool
    duration_ms: float
    files_uploaded: int = 0
    bytes_uploaded: int = 0
    target_url: str | None = None
    error: str | None = None
    error_type: str | None = None

    def __post_init__(self) -> None:
        if not self.target_name:
            raise ValueError("DeployResult.target_name must be non-empty")
        if self.duration_ms < 0:
            raise ValueError("DeployResult.duration_ms must be >= 0")
        if self.files_uploaded < 0:
            raise ValueError("DeployResult.files_uploaded must be >= 0")
        if self.bytes_uploaded < 0:
            raise ValueError("DeployResult.bytes_uploaded must be >= 0")
        if self.success and self.error:
            raise ValueError("DeployResult cannot have success=True and a non-empty error")
