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

"""Private path helpers shared across subpackages."""

from __future__ import annotations

from pathlib import Path


def _is_safe_regular_file(path: Path, root: Path) -> bool:
    """Return `True` when `path` is a non-symlink file rooted under `root`."""
    try:
        return (
            path.is_file()
            and not path.is_symlink()
            and path.resolve().is_relative_to(root.resolve())
        )
    except OSError:
        return False
