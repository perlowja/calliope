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
# See the License for the specific language governing permissions and
# limitations under the License.

"""calliope — static-site rendering substrate for adapter-driven pipelines.

Named for the Greek Muse of epic poetry, mother of Orpheus. Calliope
lifts the cleanroom page-generation stack into a standalone substrate.

Fleet position:

    clio        AI extraction primitives
    etlantis    ETL substrate
    calliope    static-site rendering  ← here
    mnemos      memory
    ↓
    adapter packages integrate domain data with the substrate

Each adapter feeds tabular or mapping-shaped data into calliope and gets
a static site out the other end. Calliope remains substrate-neutral: it
knows how to render rows as cards, compose cards into pages, bundle
assets, and deploy, but domain semantics stay in the adapter layer.

Subpackages (Phase 7 lift roadmap):

    cards       Per-row card renderers. Lifted from cleanroom
                ``card_components.py`` plus its variant family. Card
                variants share a common Protocol so apps can swap
                renderers per dimension without changing the page-level
                code.

    pages       Page-level generators. Lifted from cleanroom
                ``L1_landing_generator.py`` (single-page) and
                ``L1_metagenerator.py`` (multi-page driver). Pages
                compose cards + nav + assets into a final HTML
                document.

    templates   Jinja2 template surfaces + the ``aedifex_template``
                helper that gives card variants a reusable shell.
                Lifted from cleanroom ``aedifex_template.py`` plus
                ``frontend-templates/`` (jinja2 .html.j2 sources).

    assets      Static asset bundling — CSS, JS, images. Lifted from
                cleanroom ``assets.py`` plus ``frontend-assets/``.
                Apps register their per-page asset manifests; calliope
                produces hashed bundles + manifest-rewrites for
                cache-bust deploys.

    render      Render drivers. Lifted from cleanroom
                ``L1_render_parallel.py`` (parallel batched render)
                and ``L1_render_static_pro.py`` (production-shape
                static renderer). The ``L1_*_generator.py`` family
                becomes per-card-variant runners.

    deploy      Deploy adapters. Lifted from cleanroom
                ``deploy_tiiny.py`` (Tiiny.host upload). Future
                targets — GitHub Pages, Netlify, S3+CloudFront —
                add new modules under this package without touching
                anything else.

Status: Phase 7 Stage 1 (templates foundation) — repo scaffold,
pyproject, package shape, and template primitives are in place.
Subsequent stages lift cleanroom files into the subpackages above.
v0.0.1rc1 is the bootstrap tag (PEP 440 form); first real release
(`v0.1.0`) ships when at least cards + pages + render + deploy each
have one working primitive.
"""

__version__ = "0.0.3"
