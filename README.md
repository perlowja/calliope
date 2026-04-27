# calliope

> Static-site rendering substrate for data-journalism pipelines.

Named for the Greek Muse of epic poetry, mother of Orpheus. Calliope
provides the rendering primitives that data-journalism apps need:
per-row card renderers, page-level generators, asset bundling, render
drivers, deploy adapters. Domain-free — apps tell calliope what to
render, calliope just renders.

## Status

**`v0.1.0` — first usable release.** All six subpackages (`templates`,
`cards`, `pages`, `assets`, `render`, `deploy`) ship working substrate
primitives. Concrete domain renderers, deploy adapters, and
per-dimension page generators belong in adapter packages.

The architectural contract is documented in
[`docs/CALLIOPE-SPEC.md`](docs/CALLIOPE-SPEC.md) (§§1–17). The lift
methodology used to extract these primitives from the RiskyEats
cleanroom is in [`docs/LIFT_PATTERN.md`](docs/LIFT_PATTERN.md).

## Fleet position

```
clio        AI extraction primitives  (Muse: history)
etlantis    ETL substrate              (Atlantis)
calliope    static-site rendering      (Muse: epic poetry)  ← this repo
mnemos      memory                     (Mnemosyne)
↓
adapter packages (e.g. RiskyEats, rvmaps, weederboard) integrate
domain data with the substrate
```

Each adapter feeds tabular or mapping-shaped data into calliope and
gets a static site out the other end. Calliope itself is
substrate-neutral: it knows how to render rows, compose pages, bundle
assets, and deploy, but domain semantics stay in the adapter layer.

## Subpackages

| Module | Purpose |
|---|---|
| `calliope.templates` | Page-shell contracts: `TemplateMetadata`, `PageTemplate` ABC, `JinjaPageTemplate`, marker validation, block extraction, dependency-injected `TemplateRegistry`, sanitized HTML shell helpers. |
| `calliope.cards` | Per-row `CardRenderer` Protocol, `CardTemplate` ABC + `JinjaCardTemplate`, `Taxonomy`, `Pill`, `HeatbarSegment`, `Tier`/`TierTable`, `format_iso_date`, `slugify`. |
| `calliope.pages` | `Pagination` + `paginate()`, `Hero`, `Scoreboard`/`ScoreboardRow`, `NarrativeRenderer` Protocol + `TemplateNarrativeRenderer`, canonical block-name tuples. |
| `calliope.assets` | `Asset`, `AssetManifest`, `bundle_assets()`, `rewrite_html_with_manifest()`, SHA-256 content hashing. |
| `calliope.render` | `Renderable` Protocol, `RenderJob`, `JobOutcome`, `RenderReport`, `SerialRenderDriver`, `ThreadedRenderDriver`. Atomic file output, batch-wide duplicate-path rejection. |
| `calliope.deploy` | `DeployTarget` Protocol, `DeployResult`, `LocalDeployTarget`, `DryRunDeployTarget`. |

## Install

```bash
pip install calliope
# or for the full dev environment
pip install "calliope[dev]"
```

Optional extras: `inline` (premailer for CSS-inlined output),
`deploy` (`requests` for upcoming HTTP-based deploy adapters).

## Quick example

```python
from pathlib import Path
from calliope.assets import bundle_assets, rewrite_html_with_manifest
from calliope.deploy import LocalDeployTarget
from calliope.render import RenderJob, SerialRenderDriver

# Bundle static assets into hashed cache-busted names. The output_dir
# lives next to the rendered HTML; manifest keys are relative paths.
build = Path("build")
manifest = bundle_assets(Path("static_src"), build / "assets")

# Render pages (your `MyPage` is a `JinjaPageTemplate` subclass).
driver = SerialRenderDriver()
jobs = [
    RenderJob(name=f"page-{i}", renderable=MyPage(env), data=row,
              output_path=build / f"page-{i}.html")
    for i, row in enumerate(rows)
]
report = driver.run(jobs)
assert report.is_clean

# Rewrite HTML to point at hashed asset URLs.
# `base_path="assets/"` mirrors the on-disk layout so a logical
# `main.css` reference becomes `assets/main.<hash>.css`.
for path in build.rglob("*.html"):
    path.write_text(
        rewrite_html_with_manifest(path.read_text(), manifest, base_path="assets/")
    )

# Deploy.
LocalDeployTarget(Path("/var/www/site"), clear_existing=True).deploy(Path("build"))
```

## License

Apache 2.0. See [`LICENSE`](LICENSE).

## Provenance

Calliope was extracted from the RiskyEats cleanroom prototype as part
of Phase 7 of the substrate-decomposition project. Same lift pattern
as [`etlantis`](https://gitlab.com/perlowja/etlantis). The cleanroom
remains the historical reference. See `LIFT_PATTERN.md` and
`CALLIOPE-SPEC.md` for the contract.
