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

"""Asset — a single static file plus its content hash."""

from __future__ import annotations

from dataclasses import dataclass


def _insert_hash(logical_path: str, content_hash: str) -> str:
    """`main.css` + `a1b2c3d4` → `main.a1b2c3d4.css`."""
    if "/" in logical_path:
        directory, _, filename = logical_path.rpartition("/")
        return f"{directory}/{_insert_hash(filename, content_hash)}"
    if "." in logical_path:
        stem, _, suffix = logical_path.rpartition(".")
        return f"{stem}.{content_hash}.{suffix}"
    return f"{logical_path}.{content_hash}"


@dataclass(frozen=True)
class Asset:
    """A bundle-ready asset: logical path, raw content, content hash."""

    logical_path: str
    content: bytes
    content_hash: str
    media_type: str | None = None

    def __post_init__(self) -> None:
        if not self.logical_path:
            raise ValueError("Asset.logical_path must be non-empty")
        if self.logical_path.startswith("/"):
            raise ValueError(f"Asset.logical_path must be relative, got {self.logical_path!r}")
        if not isinstance(self.content, (bytes, bytearray)):
            raise TypeError("Asset.content must be bytes")
        if not self.content_hash:
            raise ValueError("Asset.content_hash must be non-empty")
        if not all(c in "0123456789abcdef" for c in self.content_hash):
            raise ValueError(f"Asset.content_hash must be lowercase hex, got {self.content_hash!r}")
        if not isinstance(self.content, bytes):
            object.__setattr__(self, "content", bytes(self.content))

    @property
    def published_path(self) -> str:
        """Logical path with the content hash spliced before the suffix."""
        return _insert_hash(self.logical_path, self.content_hash)

    @property
    def size(self) -> int:
        return len(self.content)
