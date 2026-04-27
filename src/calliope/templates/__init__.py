# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.templates — Jinja2 template surfaces + helpers.

Status: stub. Phase 7 Stage 2 lifts the cleanroom's template
infrastructure into this package.

Source files staged for lift:

    aedifex_template.py     (279 LOC) — template engine helpers
    ai_badge.py             (219 LOC) — AI-source badge renderer
    frontend-templates/                — jinja2 .html.j2 sources

Planned shape: a `TemplateEnvironment` class wraps Jinja2's loader,
exposes calliope-specific filters (e.g. format_date, format_number,
format_address) and globals (e.g. asset_url for asset-bundle
references). Apps register their own filters/globals by passing them
at construction.
"""
