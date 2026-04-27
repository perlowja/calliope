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

"""calliope.deploy — deploy adapters for static-site hosts.

Stage 5 ships the substrate:

- ``DeployTarget`` Protocol (runtime_checkable, structural).
- ``DeployResult`` frozen dataclass — outcome shape.
- ``LocalDeployTarget`` — copy to a local directory; the reference
  implementation.
- ``DryRunDeployTarget`` — walks the source dir, counts files +
  bytes, writes nothing.

Production deploy adapters (Tiiny.host, GitHub Pages, Netlify,
S3+CloudFront) live in adapters or external packages — calliope
ships only the contract and a working local-copy implementation.

See ``docs/CALLIOPE-SPEC.md`` §13 for the contract.
"""

from calliope.deploy.dryrun import DryRunDeployTarget
from calliope.deploy.local import LocalDeployTarget
from calliope.deploy.result import DeployResult
from calliope.deploy.target import DeployTarget

__all__ = [
    "DeployResult",
    "DeployTarget",
    "DryRunDeployTarget",
    "LocalDeployTarget",
]
