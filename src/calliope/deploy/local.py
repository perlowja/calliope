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

"""LocalDeployTarget — copies a local directory to a destination directory.

The reference deploy implementation. Useful for staging, testing, or
deploying to a mounted network share. Production deploy adapters
(Tiiny, GitHub Pages, S3, Netlify) live in adapters or external
packages.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from calliope._pathutil import _is_safe_regular_file
from calliope.deploy.result import DeployResult


class LocalDeployTarget:
    """Copy `local_dir` into `destination`, optionally clearing first."""

    def __init__(self, destination: Path, *, clear_existing: bool = False) -> None:
        if not isinstance(destination, Path):
            raise TypeError("destination must be a pathlib.Path")
        self._destination = destination
        self._clear_existing = clear_existing

    @property
    def name(self) -> str:
        return f"local:{self._destination}"

    @property
    def destination(self) -> Path:
        return self._destination

    @property
    def clear_existing(self) -> bool:
        return self._clear_existing

    def deploy(self, local_dir: Path) -> DeployResult:
        started = time.perf_counter()
        if not isinstance(local_dir, Path):
            return _failed(
                self.name,
                started,
                TypeError("local_dir must be a pathlib.Path"),
            )
        try:
            if not local_dir.is_dir():
                raise FileNotFoundError(
                    f"local_dir does not exist or is not a directory: {local_dir}"
                )

            source_root = local_dir.resolve()
            destination_root = self._destination.resolve()
            if destination_root == source_root or destination_root.is_relative_to(source_root):
                raise ValueError("destination must not be the same as or inside local_dir")

            if self._clear_existing and self._destination.exists():
                shutil.rmtree(self._destination)

            self._destination.mkdir(parents=True, exist_ok=True)

            files_uploaded = 0
            bytes_uploaded = 0
            for source in sorted(local_dir.rglob("*")):
                if not _is_safe_regular_file(source, local_dir):
                    continue
                relative = source.relative_to(local_dir)
                target = self._destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                files_uploaded += 1
                bytes_uploaded += source.stat().st_size
        except Exception as exc:  # noqa: BLE001 -- contract: never raise Exception
            return _failed(self.name, started, exc)

        return DeployResult(
            target_name=self.name,
            success=True,
            duration_ms=(time.perf_counter() - started) * 1000.0,
            files_uploaded=files_uploaded,
            bytes_uploaded=bytes_uploaded,
            target_url=str(self._destination),
        )


def _failed(target_name: str, started: float, exc: Exception) -> DeployResult:
    return DeployResult(
        target_name=target_name,
        success=False,
        duration_ms=(time.perf_counter() - started) * 1000.0,
        error=str(exc),
        error_type=type(exc).__name__,
    )
