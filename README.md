# calliope

> Static-site rendering substrate for data-journalism pipelines.

Named for the Greek Muse of epic poetry, mother of Orpheus. Calliope
provides the rendering primitives that data-journalism apps need:
per-row card renderers, page-level generators, asset bundling,
deploy adapters. Domain-free — apps tell calliope what to render,
calliope just renders.

## Status

**Phase 7 Stage 0 — repo scaffold.** Subpackage layout established;
file lifts from the RiskyEats cleanroom land in subsequent stages.
First real release (`v0.1.0`) ships when at least cards + pages +
render + deploy each have one working primitive.

## Fleet position

```
clio        AI extraction primitives  (Muse: history)
etlantis    ETL substrate              (Atlantis)
calliope    static-site rendering      (Muse: epic poetry)  ← this repo
mnemos      memory                     (Mnemosyne)
↓
RiskyEats / rvmaps / weederboard       thin adapters
```

Each adapter feeds a Polars DataFrame (typically the published
parquet output of an `etlantis` pipeline) into `calliope` and gets a
static site out the other end.

## Subpackages

| Module | Purpose | Lift source |
|---|---|---|
| `calliope.cards` | Per-row card renderers | cleanroom `card_components.py` family |
| `calliope.pages` | Page-level generators | cleanroom `L1_landing_generator.py`, `L1_metagenerator.py` |
| `calliope.templates` | Jinja2 surfaces + helpers | cleanroom `aedifex_template.py`, `frontend-templates/` |
| `calliope.assets` | Static asset bundling | cleanroom `assets.py`, `frontend-assets/` |
| `calliope.render` | Render drivers + per-dimension runners | cleanroom `L1_render_parallel.py`, `L1_render_static_pro.py`, `L1_*_generator.py` family |
| `calliope.deploy` | Deploy adapters | cleanroom `deploy_tiiny.py` |

## License

Apache 2.0. See `LICENSE`.

## Provenance

Calliope is being extracted from the RiskyEats cleanroom prototype as
part of Phase 7 of the substrate-decomposition project. Same lift
pattern as `etlantis` (extracted in early April 2026). The cleanroom
remains the historical reference; once Phase 7 ships, RiskyEats will
declare both `etlantis` AND `calliope` as deps and bare-retire
the legacy `src/`.

See `riskyeats-cleanroom/LEGACY_SRC_RETIREMENT.md` for the full
file-by-file lift roadmap.
