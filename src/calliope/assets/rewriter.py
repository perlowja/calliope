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

"""rewrite_html_with_manifest — substitute logical asset URLs in rendered HTML.

A simple regex-based rewriter that finds `href="..."`, `src="..."`, and
`url(...)` references whose path matches a key in the manifest, then
replaces the path with the manifest's published value. Adapters with
more complex rewriting needs (e.g. JS module imports, dynamic loaders)
should plug a real HTML parser and walk it themselves.
"""

from __future__ import annotations

import re

from calliope.assets.manifest import AssetManifest

_HREF_SRC_RE = re.compile(
    r"""(href|src)\s*=\s*(?P<quote>["'])(?P<path>[^"']+)(?P=quote)""",
    re.IGNORECASE,
)
_CSS_URL_RE = re.compile(
    r"""url\(\s*(?P<quote>["']?)(?P<path>[^)"']+)(?P=quote)\s*\)""",
    re.IGNORECASE,
)


def rewrite_html_with_manifest(
    html: str,
    manifest: AssetManifest,
    *,
    base_path: str = "",
) -> str:
    """Replace logical asset URLs in `html` with their manifest-published equivalents.

    `base_path` is prepended to the published path before substitution
    (e.g. `"/static/"`). The base is applied verbatim — calliope does
    not normalize trailing slashes.

    Lookup matches a path against the manifest by:
    1. The path as-is.
    2. The path with leading `./` stripped.
    3. The path with `base_path` prefix stripped (if `base_path` set).

    Paths that do not match any manifest entry are left unchanged.
    """

    def _resolve(path: str) -> str | None:
        if base_path and path.startswith(base_path):
            published = manifest.published(path[len(base_path) :])
            return f"{base_path}{published}" if published is not None else None
        if path.startswith("./"):
            published = manifest.published(path[2:])
            return f"./{published}" if published is not None else None
        published = manifest.published(path)
        if published is None:
            return None
        return f"{base_path}{published}" if base_path else published

    def _href_src_sub(match: re.Match[str]) -> str:
        attr = match.group(1)
        quote = match.group("quote")
        path = match.group("path")
        resolved = _resolve(path)
        if resolved is None:
            return match.group(0)
        return f"{attr}={quote}{resolved}{quote}"

    def _css_url_sub(match: re.Match[str]) -> str:
        quote = match.group("quote")
        path = match.group("path")
        resolved = _resolve(path)
        if resolved is None:
            return match.group(0)
        return f"url({quote}{resolved}{quote})"

    rewritten = _HREF_SRC_RE.sub(_href_src_sub, html)
    rewritten = _CSS_URL_RE.sub(_css_url_sub, rewritten)
    return rewritten
