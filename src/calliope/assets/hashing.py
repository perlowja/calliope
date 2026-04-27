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

"""Content-hash helpers used by the asset bundler.

Calliope uses SHA-256 truncated to a configurable length. The hash is
deterministic and length-stable, which keeps cache-busted asset URLs
reproducible across builds for unchanged content.
"""

from __future__ import annotations

import hashlib

DEFAULT_HASH_LENGTH = 10
MAX_HASH_LENGTH = 64
MIN_HASH_LENGTH = 4


def hash_content(data: bytes, *, length: int = DEFAULT_HASH_LENGTH) -> str:
    """Return the first `length` hex digits of SHA-256(`data`).

    `length` is constrained to `[MIN_HASH_LENGTH, MAX_HASH_LENGTH]`.
    Shorter hashes raise the chance of collision; longer ones bloat
    URLs without meaningful security benefit at the substrate layer.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"hash_content expects bytes-like, got {type(data).__name__}")
    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("hash_content.length must be int")
    if length < MIN_HASH_LENGTH:
        raise ValueError(f"hash_content.length must be >= {MIN_HASH_LENGTH}")
    if length > MAX_HASH_LENGTH:
        raise ValueError(f"hash_content.length must be <= {MAX_HASH_LENGTH}")
    return hashlib.sha256(bytes(data)).hexdigest()[:length]
