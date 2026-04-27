# Copyright 2026 calliope Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See LICENSE in the repository root for full terms.

"""calliope.deploy — deploy adapters for static-site hosts.

Status: stub. Phase 7 Stage 6 lifts the cleanroom's deploy adapter
into this package.

Source files staged for lift:

    deploy_tiiny.py     — Tiiny.host upload (cleanroom default)

Planned future targets (not staged for lift, fresh implementations
when adapters arrive):

    github_pages.py     — push to a gh-pages branch
    netlify.py          — Netlify deploy API
    s3_cloudfront.py    — S3 + CloudFront invalidation

Planned Protocol:

    DeployAdapter.deploy(site_dir: Path, target: dict[str, Any]) -> DeployResult
        Where `target` carries adapter-specific config (Tiiny site
        slug, GH repo + branch, S3 bucket + distribution ID, etc.).

The `[deploy]` extras group in pyproject pulls in `requests` for
Tiiny upload; future adapters add their own extras (e.g.
`[deploy-aws]` for boto3) so apps only install what they need.
"""
