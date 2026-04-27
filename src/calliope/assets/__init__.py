# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.assets — static asset bundling (CSS, JS, images).

Status: stub. Phase 7 Stage 2 lifts the cleanroom's asset
infrastructure into this package.

Source files staged for lift:

    assets.py             (222 LOC) — asset bundler
    frontend-assets/                 — static asset sources (CSS, JS,
                                       fonts, images)

Planned shape: an `AssetBundle` class takes a manifest of source
files, produces hashed output names + a manifest-rewrite map for
cache-bust deploys. Optional `inline=True` mode for email-shape
output uses premailer (etlantis[inline] extras) to inline CSS.
"""
