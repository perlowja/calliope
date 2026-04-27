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

"""AssetManifest — frozen mapping from logical path to published (hashed) path."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from calliope.assets.asset import Asset


@dataclass(frozen=True)
class AssetManifest:
    """Immutable lookup from `logical_path` → `published_path`.

    Adapters consult the manifest after rendering to rewrite their HTML
    so that asset references point at the cache-busted, content-hashed
    URLs.
    """

    __hash__ = None

    entries: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.entries, Mapping):
            raise TypeError("AssetManifest.entries must be a Mapping")
        for key, value in self.entries.items():
            if not isinstance(key, str):
                raise TypeError(f"AssetManifest.entries keys must be str, got {type(key).__name__}")
            if not isinstance(value, str):
                raise TypeError(
                    f"AssetManifest.entries[{key!r}] must be str, got {type(value).__name__}"
                )
        object.__setattr__(self, "entries", MappingProxyType(dict(self.entries)))

    def published(self, logical_path: str) -> str | None:
        return self.entries.get(logical_path)

    def __contains__(self, logical_path: object) -> bool:
        return isinstance(logical_path, str) and logical_path in self.entries

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterable[str]:
        return iter(self.entries)


def manifest_from_assets(assets: Iterable[Asset]) -> AssetManifest:
    """Build a manifest from a sequence of `Asset` objects.

    Raises `ValueError` if two assets share the same logical path.
    """
    entries: dict[str, str] = {}
    for asset in assets:
        if asset.logical_path in entries:
            raise ValueError(f"duplicate logical_path in asset bundle: {asset.logical_path!r}")
        entries[asset.logical_path] = asset.published_path
    return AssetManifest(entries=entries)
