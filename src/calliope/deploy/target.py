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

"""DeployTarget Protocol — the contract every deploy adapter implements."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from calliope.deploy.result import DeployResult


@runtime_checkable
class DeployTarget(Protocol):
    """Anything that can take a local directory and publish it somewhere.

    Implementations capture all errors as failed `DeployResult`s; like
    render drivers, they never raise `Exception`. `BaseException`
    (KeyboardInterrupt, SystemExit) propagates intentionally.
    """

    @property
    def name(self) -> str: ...

    def deploy(self, local_dir: Path) -> DeployResult: ...
