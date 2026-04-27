# CALLIOPE Specification

Status: `v0.1.0` — Phase 7 Stage 5 (`assets` + `deploy`) — first stable release.

Calliope is the static-site rendering substrate in the cleanroom lift
family:

```text
clio        extraction
etlantis    ETL
calliope    rendering + assets + deploy
mnemos      memory
```

Adapters feed structured data into calliope and receive HTML, static
assets, and deployable output. Domain semantics stay in adapters.

## 1. Purpose

Calliope exists to provide:

- template contracts for HTML shells,
- row-level card rendering primitives,
- page-composition primitives,
- render drivers,
- asset bundling with content-hashed filenames,
- deploy contracts and a working local reference target.

The package is substrate-neutral. It does not ship restaurant, Florida,
DBPR, or other adapter-specific literals.

## 2. Design Goals

1. Keep domain logic out of the substrate.
2. Prefer frozen data structures and defensive copies.
3. Expose small, composable interfaces instead of monolithic generators.
4. Keep output deterministic for identical inputs.
5. Capture operational errors as result objects where appropriate.
6. Leave production policy choices to adapters.

## 3. Marker Grammar

Calliope uses HTML comment markers to delimit structural blocks in
rendered output.

### 3.1 Block Names

Block names are kebab-case and match:

```text
[a-z][a-z0-9-]*
```

Opening markers:

```html
<!-- BLOCK:hero -->
<!-- BLOCK:signup optional annotation -->
```

Closing markers:

```html
<!-- /BLOCK:hero -->
```

Annotations are allowed only on opening markers.

### 3.2 Validation Semantics

`detect_blocks(html)` returns the names of paired blocks in document
order. `validate_output(html, expected_blocks, data_warnings=())`
returns a `ValidationResult` containing:

- `level`: `full`, `partial`, or `none`
- `found_blocks`
- `missing_blocks`
- `extra_blocks`
- `out_of_order`
- `duplicate_blocks`
- `unclosed_blocks`
- `data_warnings`

Sequence matters. Validation checks order, not just membership.

## 4. Templates Overview

`calliope.templates` defines page-shell contracts and reusable helpers.
Templates operate on one mapping at a time. Pagination, batching, and
parallelism belong to later stages.

The templates layer exports:

- `TemplateMetadata`
- `PageTemplate`
- `JinjaPageTemplate`
- `bind_data`
- `safe_value`
- `detect_blocks`
- `validate_output`
- `extract_blocks`
- `TemplateRegistry`

## 5. Template Metadata And Rendering

### 5.1 TemplateMetadata

```python
@dataclass(frozen=True)
class TemplateMetadata:
    template_name: str
    version: str
    blocks: tuple[str, ...]
    required_fields: tuple[str, ...] = ()
    optional_fields: tuple[str, ...] = ()
    fallbacks: Mapping[str, Any] = field(default_factory=dict)
```

`TemplateMetadata` is an immutable page-shell contract.

- `template_name` and `version` must be non-empty.
- `blocks` is an ordered tuple and must be unique.
- `fallbacks` is defensively copied into a `MappingProxyType`.
- the class is explicitly unhashable.

### 5.2 Data Binding

```python
def safe_value(value: Any, *, escape_html: bool = True) -> str: ...

def bind_data(
    metadata: TemplateMetadata,
    data: Mapping[str, Any],
    *,
    strict: bool = True,
) -> tuple[Mapping[str, Any], tuple[str, ...]]: ...
```

`bind_data` preserves undeclared keys. Metadata is a contract for
required and optional fields, not a whitelist. In strict mode, missing
required fields raise `ValueError`. In lenient mode, fallbacks are used
and warnings are returned.

### 5.3 PageTemplate

```python
class PageTemplate(ABC):
    @property
    def metadata(self) -> TemplateMetadata: ...
    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...
```

`PageTemplate` is the abstract page-shell contract.

### 5.4 JinjaPageTemplate

```python
class JinjaPageTemplate(PageTemplate):
    jinja_template_name: str = ""
```

`JinjaPageTemplate` binds data and context into a Jinja2 environment.
Subclasses must set `jinja_template_name` and provide `metadata`.
Subclasses must not mutate caller-supplied `data`.

## 6. Validation And Extraction

```python
def detect_blocks(html: str) -> tuple[str, ...]: ...
def validate_output(
    html: str,
    expected_blocks: Iterable[str],
    data_warnings: Iterable[str] = (),
) -> ValidationResult: ...
def extract_blocks(html: str) -> Mapping[str, str]: ...
```

`extract_blocks` returns block-name to inner-HTML mappings for paired,
non-duplicate blocks. Duplicate names are intentionally suppressed from
the extracted mapping; callers consult `ValidationResult.duplicate_blocks`
when that distinction matters.

## 7. Registry And Shell Helpers

### 7.1 TemplateRegistry

```python
class TemplateRegistry:
    def register(self, template: PageTemplate, *, replace: bool = False) -> None: ...
    def get(self, template_name: str, version: str | None = None) -> PageTemplate: ...
```

There is no global registry. Adapters construct and inject a
`TemplateRegistry` instance. Template versions use PEP 440 ordering via
`packaging.version.Version`; `get(name)` without a version selects the
highest registered version.

### 7.2 Shell Helpers

`calliope.templates.shell` provides parameterized HTML-shell helpers.
These are utilities, not domain templates, and must remain free of
adapter branding and jurisdiction-specific strings.

## 8. RenderResult

```python
@dataclass(frozen=True)
class RenderResult:
    template_name: str
    template_version: str
    html_output: str
    blocks: Mapping[str, str]
    validation: ValidationResult
    render_time_ms: float
```

`RenderResult` is produced by render-stage code, not by templates
directly. It remains in `calliope.render` so the templates layer does
not import render-driver concerns.

## 9. Cards

`calliope.cards` ships substrate primitives for row-level rendering.

### 9.1 CardRenderer Protocol

`CardRenderer` is a runtime-checkable structural protocol for anything
that can render a single row mapping to HTML.

### 9.2 CardTemplate Bases

`CardTemplate` is the abstract base. `JinjaCardTemplate` is the Jinja2
implementation for row-oriented rendering.

### 9.3 Taxonomy

`TaxonomyEntry` and `Taxonomy` capture domain-key to display-attribute
lookups. Entries are defensively copied and the mapping-bearing class is
explicitly unhashable.

### 9.4 Pills

`Pill`, `render_pill`, and `render_pills` provide inline badge
renderers. `Pill.from_taxonomy(entry)` supports the common taxonomy
lookup path.

### 9.5 Heatbars

`HeatbarSegment` and `render_heatbar()` render weighted, segmented fill
bars. Score calculation stays in adapters; calliope only renders.

### 9.6 Tiers

`Tier`, `TierTable`, and `make_tier_table()` classify scores into
labels. Boundary and sorting behavior are defined by the table, not by
adapter conventions.

### 9.7 Formatting Helpers

`format_iso_date` and `slugify` are pure helpers with no domain
knowledge.

## 10. Pages

`calliope.pages` ships substrate-shaped page-composition primitives.

### 10.1 Pagination

`Pagination`, `PaginationPage`, and `paginate()` split iterables into
1-based pages. Empty input still emits one page with `total_pages=1`.

### 10.2 Hero

`Hero` and `render_hero()` render the above-the-fold section and emit a
`hero` block marker pair.

### 10.3 Scoreboard

`ScoreboardRow`, `Scoreboard`, `make_scoreboard()`, and
`render_scoreboard()` render titled tabular summaries and emit a
`scoreboard` block marker pair.

### 10.4 Narrative

`NarrativeRenderer` is a protocol. `TemplateNarrativeRenderer` is the
Jinja2-backed implementation. AI- or model-driven narrative generators
belong in adapters.

### 10.5 Canonical Block Tuples

`INDEX_PAGE_BLOCKS`, `LIST_PAGE_BLOCKS`, `DIMENSION_PAGE_BLOCKS`, and
`DETAIL_PAGE_BLOCKS` provide reusable ordered block contracts for page
templates.

## 11. Render Drivers

`calliope.render` executes batches of render jobs.

### 11.1 Renderable And RenderDriver Protocols

```python
@runtime_checkable
class Renderable(Protocol):
    @property
    def metadata(self) -> TemplateMetadata: ...
    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...

@runtime_checkable
class RenderDriver(Protocol):
    def run(self, jobs: Iterable[RenderJob]) -> RenderReport: ...
```

`Renderable` is satisfied structurally by page templates, card
templates, and matching adapter classes.

### 11.2 RenderJob

```python
@dataclass(frozen=True)
class RenderJob:
    name: str
    renderable: Renderable
    data: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] | None = None
    output_path: Path | None = None
```

`data` and `context` are defensively copied into read-only mappings.
`output_path=None` means the rendered HTML is returned in the report and
not written to disk.

### 11.3 JobOutcome And RenderReport

Drivers return `RenderReport(outcomes=...)`, where each `JobOutcome`
captures success, duration, optional `output_path`, optional
`html_output`, and optional error information.

Drivers capture `Exception` subclasses into failed outcomes. `BaseException`
subclasses propagate intentionally.

### 11.4 SerialRenderDriver

Runs jobs one at a time and returns outcomes in input order.

### 11.5 ThreadedRenderDriver

Runs jobs through `ThreadPoolExecutor` and also returns outcomes in
input order. Parent directories are created automatically for
file-backed jobs. File writes are atomic at the render-driver layer.

## 12. Assets

`calliope.assets` ships static asset bundling with content-hashed
filenames.

### 12.1 Asset

```python
@dataclass(frozen=True)
class Asset:
    logical_path: str
    content: bytes
    content_hash: str
    media_type: str | None = None
```

`logical_path` must be relative and non-empty. `content_hash` must be
non-empty lowercase hex. `published_path` inserts the hash before the
final suffix, preserving subdirectories.

### 12.2 Hashing

```python
DEFAULT_HASH_LENGTH = 10
MIN_HASH_LENGTH = 4
MAX_HASH_LENGTH = 64

def hash_content(data: bytes, *, length: int = DEFAULT_HASH_LENGTH) -> str: ...
```

Calliope uses SHA-256 truncated to `length`. The hash is deterministic
and length-stable.

### 12.3 AssetManifest

```python
@dataclass(frozen=True)
class AssetManifest:
    entries: Mapping[str, str]

def manifest_from_assets(assets: Iterable[Asset]) -> AssetManifest: ...
```

`AssetManifest` is an immutable lookup from logical path to published
path. Entries are stored in a `MappingProxyType`, the class is
explicitly unhashable, and duplicate logical paths are rejected.

### 12.4 Bundling

```python
def collect_assets(
    source_dir: Path,
    *,
    hash_length: int = DEFAULT_HASH_LENGTH,
    excludes: Iterable[str] = (),
) -> tuple[Asset, ...]: ...

def bundle_assets(
    source_dir: Path,
    output_dir: Path,
    *,
    hash_length: int = DEFAULT_HASH_LENGTH,
    excludes: Iterable[str] = (),
) -> AssetManifest: ...
```

`collect_assets` reads every safe regular file under `source_dir` and
returns `Asset` tuples. Symlinks are always rejected, even when they
resolve back into `source_dir`. `excludes` skips either an exact
relative file path or an entire relative subtree.

`bundle_assets` additionally writes each asset to
`output_dir/<published_path>` and returns the manifest.

When `output_dir` resolves inside `source_dir`, `bundle_assets`
automatically adds the output directory's source-relative path to
`excludes` before walking the tree. That makes reruns idempotent for
nested outputs such as `bundle_assets(src, src / "dist")`.

Calliope intentionally does not minify, compile, or transform asset
content. Adapters that need bundling preprocess their source directory
before calling `bundle_assets`.

### 12.5 HTML Rewriting

```python
def rewrite_html_with_manifest(
    html: str,
    manifest: AssetManifest,
    *,
    base_path: str = "",
) -> str: ...
```

Regex-based substitution of `href="..."`, `src="..."`, and `url(...)`
references. When `base_path` is set, both bare logical paths
(`main.css`) and prefixed paths (`/static/main.css`) resolve to the
prefixed published form (`/static/main.abcd.css`). When `base_path` is
empty, bare paths resolve as-is and `./logical-path` is preserved.

Adapters with more complex rewriting needs, such as JS module imports,
dynamic loaders, or Subresource Integrity handling, should use a real
HTML parser.

## 13. Deploy

`calliope.deploy` ships the substrate. Production deploy adapters
(Tiiny.host, GitHub Pages, Netlify, S3+CloudFront) live in adapters or
external packages.

### 13.1 DeployTarget Protocol

```python
@runtime_checkable
class DeployTarget(Protocol):
    @property
    def name(self) -> str: ...
    def deploy(self, local_dir: Path) -> DeployResult: ...
```

Implementations capture all errors as failed `DeployResult`s and never
raise `Exception`. `BaseException` propagates intentionally.

### 13.2 DeployResult

```python
@dataclass(frozen=True)
class DeployResult:
    target_name: str
    success: bool
    duration_ms: float
    files_uploaded: int = 0
    bytes_uploaded: int = 0
    target_url: str | None = None
    error: str | None = None
    error_type: str | None = None
```

`target_name` must be non-empty. `duration_ms`, `files_uploaded`, and
`bytes_uploaded` must be non-negative. `success=True` excludes a
non-empty `error`.

### 13.3 LocalDeployTarget

```python
class LocalDeployTarget:
    def __init__(self, destination: Path, *, clear_existing: bool = False): ...
```

Copies every safe regular file under `local_dir` into `destination`,
preserving subdirectory layout and file metadata via `shutil.copy2`.
Symlinks are always skipped, even when they resolve back into
`local_dir`. When `clear_existing=True`, the existing destination is
removed first with `shutil.rmtree`. Default behavior preserves any
existing files already present at the destination.

Deploy fails with a `ValueError` result when `destination` resolves to
the same directory as `local_dir` or a descendant of it, preventing
self-copy recursion (`destination/destination/...`).

Atomic replacement and rollback on mid-copy failure remain future work
and are intentionally not implemented in this stage.

### 13.4 DryRunDeployTarget

```python
class DryRunDeployTarget:
    @property
    def name(self) -> str = "dryrun"
```

Walks `local_dir`, counts safe regular files and total bytes, writes
nothing, and returns a successful `DeployResult` with `target_url=None`.
Symlinks are always skipped, even when they resolve back into
`local_dir`.

## 14. Stage Map

| Stage | Subpackage | Lift sources |
|---|---|---|
| 1 | `templates` | spec; `aedifex_template.py` (sanitized helpers); production marker fixtures from `L1_metagenerator.py` |
| 2 | `cards` | substrate primitives designed from spec; `card_components.py` family is reference material, not lift source |
| 3 | `pages` | substrate primitives (pagination, hero, scoreboard, narrative); `L1_landing_generator.py` / `L1_metagenerator.py` / `L1_narrative.py` are reference material |
| 4 | `render` | substrate primitives (`Renderable`, `RenderJob`, `RenderDriver`, `SerialRenderDriver`, `ThreadedRenderDriver`) |
| 5 | `assets` + `deploy` | substrate primitives (`Asset`, `AssetManifest`, `bundle_assets`, `rewrite_html_with_manifest`; `DeployTarget`, `DeployResult`, `LocalDeployTarget`, `DryRunDeployTarget`) |
| 6 | tag `calliope v0.1.0` | first stable release; gated on cards + pages + render + deploy each having a working primitive |

See `docs/LIFT_PATTERN.md` for per-file lift methodology.

## 15. Versioning

- Major: structural change to marker grammar, `TemplateMetadata`
  shape, or subpackage boundaries.
- Minor: new primitives or features that preserve existing contracts.
- Patch: bug fixes, documentation, fallback tweaks, and internal
  refactors.

Calliope follows PEP 440. The first stable tag is `v0.1.0`.

## 16. Security Posture

Calliope is a local rendering substrate, not a sandbox.

- Template rendering trusts the adapter-selected template environment.
- HTML rewriting is regex-based and intentionally narrow.
- Asset and deploy walkers reject symlinked files.
- No credential storage or remote deploy logic ships in the substrate.
- Adapters are responsible for CSP, sanitization policy, secret
  management, and network-facing security controls.

## 17. What Calliope Is Not

Calliope is not:

- a CMS,
- a full JavaScript or CSS build pipeline,
- a domain data model,
- a production deploy orchestrator,
- an HTML sanitizer,
- an adapter registry or app framework.

Its job is to provide stable rendering, asset, and deploy primitives so
adapters can compose policy and domain behavior on top.
