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

"""calliope.assets — static asset bundling with content-hashed names.

Stage 5 ships:

- ``Asset`` + ``hash_content`` — asset model and SHA-256-based hashing.
- ``AssetManifest`` + ``manifest_from_assets`` — frozen lookup of
  logical → published paths.
- ``collect_assets`` and ``bundle_assets`` — read source dir, write
  hashed copies, return manifest.
- ``rewrite_html_with_manifest`` — substitute logical URLs in rendered
  HTML with published (cache-busted) URLs.

Calliope intentionally does not minify, compile, or transform asset
content; it only hashes and rewrites. Adapters that need bundling
preprocess their source dir before calling ``bundle_assets``.

See ``docs/CALLIOPE-SPEC.md`` §12 for the contract.
"""

from calliope.assets.asset import Asset
from calliope.assets.bundler import bundle_assets, collect_assets
from calliope.assets.hashing import (
    DEFAULT_HASH_LENGTH,
    MAX_HASH_LENGTH,
    MIN_HASH_LENGTH,
    hash_content,
)
from calliope.assets.manifest import AssetManifest, manifest_from_assets
from calliope.assets.rewriter import rewrite_html_with_manifest

__all__ = [
    "Asset",
    "AssetManifest",
    "DEFAULT_HASH_LENGTH",
    "MAX_HASH_LENGTH",
    "MIN_HASH_LENGTH",
    "bundle_assets",
    "collect_assets",
    "hash_content",
    "manifest_from_assets",
    "rewrite_html_with_manifest",
]
