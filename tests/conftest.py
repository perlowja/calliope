# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Test fixtures, including production marker samples lifted verbatim
from upstream cleanroom output.
"""

from __future__ import annotations

import pytest

PRODUCTION_PAGE_FIXTURE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Sample - Demo</title>
</head>
<body>
    <!-- BLOCK:header -->
    <h1>Header content</h1>
    <!-- /BLOCK:header -->

    <!-- BLOCK:nav -->
    <nav>Navigation</nav>
    <!-- /BLOCK:nav -->

    <!-- BLOCK:how-to-use (placeholder - prevents layout shift) -->
    <div class="placeholder">How to use</div>
    <!-- /BLOCK:how-to-use -->

    <div class="container">
        <!-- BLOCK:stats -->
        <div class="stats-grid">…</div>
        <!-- /BLOCK:stats -->
    </div>

    <!-- BLOCK:signup (placeholder for MailerLite - prevents layout shift) -->
    <div class="signup-placeholder">…</div>
    <!-- /BLOCK:signup -->

    <!-- BLOCK:news (RSS feed - dimension-themed) -->
    <div class="news">…</div>
    <!-- /BLOCK:news -->

    <div class="container">
        <!-- BLOCK:content -->
        <article>Body</article>
        <!-- /BLOCK:content -->

        <!-- BLOCK:legal -->
        <div class="legal-block">…</div>
        <!-- /BLOCK:legal -->
    </div>

    <!-- BLOCK:footer -->
    <footer>Site footer</footer>
    <!-- /BLOCK:footer -->
</body>
</html>
"""

PRODUCTION_BLOCK_ORDER = (
    "header",
    "nav",
    "how-to-use",
    "stats",
    "signup",
    "news",
    "content",
    "legal",
    "footer",
)


@pytest.fixture
def production_page() -> str:
    return PRODUCTION_PAGE_FIXTURE


@pytest.fixture
def production_block_order() -> tuple[str, ...]:
    return PRODUCTION_BLOCK_ORDER
