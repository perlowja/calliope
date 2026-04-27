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

"""bundle_assets — read source dir, write hashed copies, return manifest.

Subset of a typical asset pipeline: takes a directory of static files
and emits the same shape into an output directory with content-hashed
filenames. Returns an `AssetManifest` for HTML rewriting.

Calliope intentionally does NOT bundle/minify/compile (no SCSS, no JS
bundling, no PostCSS). Adapters that want minification preprocess
their source dir before calling `bundle_assets`.
"""

from __future__ import annotations

import mimetypes
from collections.abc import Iterable
from pathlib import Path

from calliope._pathutil import _is_safe_regular_file
from calliope.assets.asset import Asset
from calliope.assets.hashing import DEFAULT_HASH_LENGTH, hash_content
from calliope.assets.manifest import AssetManifest, manifest_from_assets


def _is_excluded_path(relative: str, excluded: set[str]) -> bool:
    return any(
        entry == "." or relative == entry or relative.startswith(f"{entry}/") for entry in excluded
    )


def collect_assets(
    source_dir: Path,
    *,
    hash_length: int = DEFAULT_HASH_LENGTH,
    excludes: Iterable[str] = (),
) -> tuple[Asset, ...]:
    """Read every regular file under `source_dir` and return `Asset`s.

    `logical_path` is the path relative to `source_dir`, joined with `/`.
    `excludes` is a sequence of relative paths to skip.
    """
    if not source_dir.is_dir():
        raise FileNotFoundError(f"source_dir does not exist or is not a directory: {source_dir}")
    excluded = {Path(e).as_posix() for e in excludes}

    assets: list[Asset] = []
    for path in sorted(source_dir.rglob("*")):
        if not _is_safe_regular_file(path, source_dir):
            continue
        relative = path.relative_to(source_dir).as_posix()
        if _is_excluded_path(relative, excluded):
            continue
        content = path.read_bytes()
        digest = hash_content(content, length=hash_length)
        media_type, _ = mimetypes.guess_type(relative)
        assets.append(
            Asset(
                logical_path=relative,
                content=content,
                content_hash=digest,
                media_type=media_type,
            )
        )
    return tuple(assets)


def bundle_assets(
    source_dir: Path,
    output_dir: Path,
    *,
    hash_length: int = DEFAULT_HASH_LENGTH,
    excludes: Iterable[str] = (),
) -> AssetManifest:
    """Bundle `source_dir` to `output_dir`; return the manifest.

    For each file under `source_dir`, this writes a copy at
    `output_dir/<published_path>` (with the hash spliced before the
    extension). The manifest maps `logical_path` → `published_path`.
    """
    if not isinstance(source_dir, Path):
        raise TypeError("source_dir must be a pathlib.Path")
    if not isinstance(output_dir, Path):
        raise TypeError("output_dir must be a pathlib.Path")

    effective_excludes = {Path(e).as_posix() for e in excludes}
    source_root = source_dir.resolve()
    output_root = output_dir.resolve()
    if output_root.is_relative_to(source_root):
        effective_excludes.add(output_root.relative_to(source_root).as_posix())

    assets = collect_assets(source_dir, hash_length=hash_length, excludes=effective_excludes)
    output_dir.mkdir(parents=True, exist_ok=True)
    for asset in assets:
        target = output_dir / asset.published_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(asset.content)
    return manifest_from_assets(assets)
