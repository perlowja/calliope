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

"""calliope — static-site rendering substrate for data-journalism pipelines.

Named for the Greek Muse of epic poetry, mother of Orpheus. Calliope
lifts the cleanroom's `L*_*_generator.py` family + `card_components.py`
+ `aedifex_template.py` + `ai_badge.py` + `assets.py` +
`frontend-templates/` + `frontend-assets/` into a standalone substrate.

Fleet position:

    clio        AI extraction primitives  (Muse: history)
    etlantis    ETL substrate              (Atlantis)
    calliope    static-site rendering      (Muse: epic poetry)  ← here
    mnemos      memory                     (Mnemosyne)
    ↓
    RiskyEats / rvmaps / weederboard       thin adapters

Each adapter feeds a Polars DataFrame (typically the published parquet
output of an etlantis pipeline) into calliope and gets a static site
out the other end. No domain coupling: calliope doesn't know what
DBPR is, doesn't know what a "restaurant" is, doesn't know what
"chronic violations" mean. It knows how to render a row as a card,
compose cards into pages, bundle assets, and deploy.

Subpackages (Phase 7 lift roadmap):

    cards       Per-row card renderers. Lifted from cleanroom
                ``card_components.py`` + ``badactors_card_components.py``
                + ``codered_card_components{,_v2}.py`` +
                ``defunct_card_components.py``. Card variants share a
                common Protocol so apps can swap renderers per
                dimension without changing the page-level code.

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
                static renderer). Plus the per-dimension page
                generators (L1_badactors_generator, L1_chronic_generator,
                L1_cleanplates_generator, …) which become per-card-
                variant runners.

    deploy      Deploy adapters. Lifted from cleanroom
                ``deploy_tiiny.py`` (Tiiny.host upload). Future
                targets — GitHub Pages, Netlify, S3+CloudFront —
                add new modules under this package without touching
                anything else.

Status: Phase 7 Stage 0 (this commit) — repo scaffold, pyproject,
package shape. Subsequent stages lift cleanroom files into the
subpackages above. v0.0.1rc1 is the bootstrap tag (PEP 440 form);
first real release (v0.1.0) ships when at least cards + pages +
render + deploy each have one working primitive.
"""

__version__ = "0.0.1rc1"
