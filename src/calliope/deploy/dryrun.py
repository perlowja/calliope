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

"""DryRunDeployTarget — walks the local dir and reports what would deploy."""

from __future__ import annotations

import time
from pathlib import Path

from calliope._pathutil import _is_safe_regular_file
from calliope.deploy.result import DeployResult


class DryRunDeployTarget:
    """Counts files and bytes under `local_dir` without writing anywhere.

    Useful in CI smoke tests and as a pre-deploy sanity check. Adapter
    code can swap a real `DeployTarget` for `DryRunDeployTarget()` to
    confirm the asset bundle and HTML output are well-formed before
    any network traffic.
    """

    @property
    def name(self) -> str:
        return "dryrun"

    def deploy(self, local_dir: Path) -> DeployResult:
        started = time.perf_counter()
        if not isinstance(local_dir, Path):
            return DeployResult(
                target_name=self.name,
                success=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                error="local_dir must be a pathlib.Path",
                error_type="TypeError",
            )
        try:
            if not local_dir.is_dir():
                raise FileNotFoundError(
                    f"local_dir does not exist or is not a directory: {local_dir}"
                )
            files = 0
            total_bytes = 0
            for entry in sorted(local_dir.rglob("*")):
                if not _is_safe_regular_file(entry, local_dir):
                    continue
                files += 1
                total_bytes += entry.stat().st_size
        except Exception as exc:  # noqa: BLE001
            return DeployResult(
                target_name=self.name,
                success=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                error=str(exc),
                error_type=type(exc).__name__,
            )

        return DeployResult(
            target_name=self.name,
            success=True,
            duration_ms=(time.perf_counter() - started) * 1000.0,
            files_uploaded=files,
            bytes_uploaded=total_bytes,
            target_url=None,
        )
