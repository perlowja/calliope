# Calliope Specification

**Status:** v0.1 — Phase 7 Stage 3 (pages)
**Reference:** AEDIFEX/ASSG (2025-12-09) — used as a guide, not adopted wholesale.

---

## 1. Purpose

Calliope is a static-site rendering substrate for data-journalism pipelines.
It accepts caller-supplied row data (typically Polars DataFrames published by
an ETL pipeline) and emits HTML pages, asset bundles, and deploy artifacts.

It is intentionally domain-agnostic: it does not know what a restaurant is,
what a "violation" means, or what jurisdiction the data describes. Domain
shape lives in adapters (e.g. RiskyEats, rvmaps, weederboard).

## 2. Subpackage layout

Each subpackage has a single, narrow responsibility. The split is the
substrate's primary architectural commitment and is not collapsed into a
single namespace.

| Subpackage | Responsibility |
|---|---|
| `calliope.templates` | Page-shell contracts: metadata, marker validation, block extraction, registry, sanitized shell helpers |
| `calliope.cards` | Per-row card renderers via a swappable Protocol |
| `calliope.pages` | Page-level generators that compose cards + nav + assets |
| `calliope.assets` | Static asset bundling, hashing, and manifest rewrites |
| `calliope.render` | Render drivers (parallel batched, production static) and `RenderResult` |
| `calliope.deploy` | Deploy adapters (Tiiny.host, GitHub Pages, S3+CloudFront, …) |

A page template is **not** a card template. A card renderer is **not** a page
generator. They have different lifecycles, different inputs, and different
outputs, and they live in different subpackages.

## 3. Marker grammar

Calliope adopts the AEDIFEX block-marker convention but defines its own
grammar — strict enough to validate, permissive enough to match production
output already shipped by upstream adapters.

### 3.1 Opening marker

```
<!-- BLOCK:<name>[ <annotation>] -->
```

- `name`: kebab-case, `[a-z][a-z0-9-]*` (matches `header`, `nav`, `how-to-use`,
  `red-alert`).
- `annotation` *(optional)*: free-form text after a single space, terminated
  by `-->`. Conventionally a parenthesized note like
  `(placeholder - prevents layout shift)` or `(RSS feed - dimension-themed)`.
  Annotations are documentation; calliope ignores them when matching.

### 3.2 Closing marker

```
<!-- /BLOCK:<name> -->
```

- `name`: same kebab-case grammar as opening.
- No annotation. A closing marker with annotation is a parse error.

### 3.3 Validation

A page is **structurally compliant** with a template iff:

1. Every name in `metadata.blocks` appears as an opening marker exactly once.
2. Every opening marker is followed later in document order by a matching
   closing marker; a close-before-open marker does not satisfy the block.
3. The order of opening markers in the rendered HTML matches the order of
   `metadata.blocks`.
4. No marker appears that is not declared in `metadata.blocks` (extra-block).

Compliance levels:

| Level | Meaning |
|---|---|
| `FULL` | All four conditions hold. |
| `PARTIAL` | Markers found, but at least one of (missing, extra, out-of-order, duplicate, unclosed). |
| `NONE` | No recognizable markers in the output. |

`PARTIAL` is usable but should be reported. `NONE` is a render failure.

#### Duplicate suppression contract

A block name that appears more than once as an opening marker is treated
as a single classification — `duplicate_blocks` — and is **suppressed
from pairing**, with the following observable behavior:

| Surface | Behavior for a duplicate name |
|---|---|
| `ValidationResult.duplicate_blocks` | Reports the name. |
| `ValidationResult.found_blocks` | Does not include the name. |
| `ValidationResult.unclosed_blocks` | Does not include the name even if some opens are unclosed. Duplicate trumps unclosed. |
| `ValidationResult.missing_blocks` | Includes the name if it appears in `expected_blocks`, because the name is absent from `found_blocks`. Missing and duplicate are independent classifications and may both apply. |
| `ValidationResult.extra_blocks` | Does not include the name. A duplicate name that is *not* in `expected_blocks` is reported only via `duplicate_blocks`, not via `extra_blocks`, because `extra_blocks` is computed from `found_blocks` after duplicate suppression. |
| `validate_output()` compliance level | `PARTIAL` (never `FULL`, never silently). |
| `detect_blocks(html)` | Does not include the name. |
| `extract_blocks(html, names)` | Returns `""` for the name. |
| `extract_blocks(html)` (default) | Omits the name from the result mapping. |

The rationale is that duplicate same-name blocks are always a render bug;
exposing one of them to consumers as canonical would corrupt downstream
data, and reporting them as both `duplicate` and `unclosed` would
double-count the same defect. Consumers that need to debug a duplicate
open inspect `ValidationResult.duplicate_blocks` directly. Consumers
checking strict compliance use `is_compliant`, which is `False` whenever
any of `duplicate_blocks`, `missing_blocks`, `extra_blocks`,
`out_of_order`, or `unclosed_blocks` is non-empty.

### 3.4 Why this grammar (and not the AEDIFEX spec's)

The AEDIFEX reference validator used `(\w+)` for name capture and exact-string
search for opening markers. That validator would reject already-shipped
production output that uses hyphenated names (`how-to-use`) and annotated
openings (`signup (placeholder for MailerLite - prevents layout shift)`).
Calliope's grammar accepts the production shape so existing pages migrate
without false-failure noise.

## 4. Template metadata

```python
@dataclass(frozen=True)
class TemplateMetadata:
    template_name: str          # e.g. "page.dimension"
    version: str                # PEP 440 / SemVer
    blocks: tuple[str, ...]     # ordered, unique
    required_fields: tuple[str, ...] = ()
    optional_fields: tuple[str, ...] = ()
    fallbacks: Mapping[str, Any] = MappingProxyType({})
```

Tuples (not lists) and a `MappingProxyType` wrapped around a defensive copy
make metadata immutable. `TemplateMetadata` is not hashable because
`fallbacks` accepts arbitrary mapping values. `blocks` is **ordered** — the
validator checks order, not just membership. `template_name` uses a dotted
namespace; the segment before the first dot is the rendering category
(`page`, `card`, `asset`).

The metadata is the page-shell contract. It is **not** the full data
contract. Page-specific render context (CSS paths, navigation items, asset
hashes) is supplied at render time as additional context, not declared in
metadata. This is the deliberate departure from the AEDIFEX reference
`bind_data()`, which only preserved metadata-declared keys and forced sample
templates to use a second `default_context` channel.

## 5. PageTemplate ABC

```python
class PageTemplate(ABC):
    @property
    @abstractmethod
    def metadata(self) -> TemplateMetadata: ...

    @abstractmethod
    def render(
        self,
        data: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...
```

`render` accepts any `Mapping[str, Any]` — including dicts, `MappingProxyType`,
or per-row mappings derived from `df.iter_rows(named=True)`. Subclasses must
not mutate `data`. Calliope ships `JinjaPageTemplate(PageTemplate)` as the
recommended concrete base; subclasses provide a Jinja `Environment` and
`jinja_template_name` loader key and override `bind_context()` to shape
per-page data.

## 6. Polars boundary

Calliope does not call any Polars constructor. Adapters supply data; calliope
consumes it.

| Stage | Polars role |
|---|---|
| Card render | Adapter calls `df.iter_rows(named=True)` and feeds each `dict` to a card renderer. |
| Page render | Adapter computes per-page aggregates and passes `Mapping[str, Any]`. |
| Render driver (Stage 5+) | Operates on iterables of pages; never materializes the full site eagerly. |

`bind_data()` operates on a single `Mapping[str, Any]` and returns a single
bound mapping plus warnings. There is no list-of-pages variant. Pagination
lives in `calliope.render`, not in `calliope.templates`.

## 7. Registry

`calliope.templates.registry.TemplateRegistry` is a minimal dependency-injected
store of templates keyed by `(template_name, version)`. There is no global
singleton; adapters or test fixtures construct one and inject it where needed.

Versions are validated at `register()` time via `packaging.version.Version`.
Registering the same `(template_name, version)` twice raises `ValueError`
unless `register(..., replace=True)` is used explicitly.

Multi-version coexistence is supported by the data model (`(name, version)`
key) but is not enforced or required at Stage 1. The reference AEDIFEX
registry sorted by lexicographic string and exposed a mutable global; both
choices are explicitly rejected. When selection among versions is needed,
comparison goes through `packaging.version.Version`, not string sort.

## 8. Render results

`RenderResult` lives in `calliope.render.results`, **not** in
`calliope.templates`. Templates produce HTML; the render driver produces
results. Mixing the two coupled bind / render / validate / extract / write
into one mutable object in the AEDIFEX reference; Calliope keeps these
concerns separate.

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

## 9. Cards

`calliope.cards` ships substrate primitives for per-row card renderers.
The cleanroom card sources are domain-coupled to DBPR / Florida / RiskyEats
taxonomies; calliope retains only the substrate abstractions and pushes
domain literals into adapters.

### 9.1 CardRenderer Protocol

```python
@runtime_checkable
class CardRenderer(Protocol):
    @property
    def metadata(self) -> TemplateMetadata: ...
    def render(
        self,
        row: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> str: ...
```

Per-row semantics: `render()` is called once per data row with that
row's mapping. Site-level aggregates and navigation belong in
`calliope.pages`, not here. The Protocol is `runtime_checkable` so
adapters can pick a renderer by structural match without subclassing.

### 9.2 CardTemplate ABC + JinjaCardTemplate

`CardTemplate` mirrors `PageTemplate` (metadata + render + the same
helpers `expected_blocks` and `required_fields`) but with per-row
semantics. `JinjaCardTemplate` is the concrete Jinja2-aware base;
subclasses set `jinja_template_name` and override `bind_context()` to
shape the per-row mapping before rendering.

### 9.3 Taxonomy

```python
@dataclass(frozen=True)
class TaxonomyEntry:
    label: str
    css_class: str = ""
    color: str | None = None

@dataclass(frozen=True)
class Taxonomy:
    name: str
    entries: Mapping[str, TaxonomyEntry]
    fallback: TaxonomyEntry
```

Subsumes the cleanroom pattern of repeated per-domain dicts
(`LICENSE_TYPE_MAP`, `INSPECTION_TYPE_MAP`, `DISPOSITION_MAP`,
`ENTITY_TYPE_MAP`). Adapters supply concrete entries; calliope ships
zero domain-specific taxonomy data. Defensive-copy semantics match
`TemplateMetadata`: entries are stored in a `MappingProxyType`, the
class is explicitly unhashable. Keys are string-only; non-`str` keys are
rejected at construction, and lookup does not coerce key types.

### 9.4 Pill

```python
@dataclass(frozen=True)
class Pill:
    label: str
    css_class: str = ""
    color: str | None = None
    title: str | None = None
```

`render_pill(pill)` and `render_pills(pills)` produce the inline-badge
HTML that adapters compose into card bodies. `Pill.from_taxonomy()`
adapts a `TaxonomyEntry` into a `Pill` for the common
"taxonomy-lookup → render" path. Labels are HTML-escaped via
`templates.safe_value`.

### 9.5 Heatbar

```python
@dataclass(frozen=True)
class HeatbarSegment:
    weight: float
    css_class: str = ""
    color: str | None = None
    title: str | None = None
```

`render_heatbar(segments, fill_pct=…)` renders a colored bar that fills
`fill_pct` percent of its container width. Segments split that filled
width proportionally by `weight`. `fill_pct` is clamped to `[0, 100]`;
zero-weight and non-finite-weight segments are skipped. Score
*calculation* lives in adapters; calliope only renders.

### 9.6 Tier classification

```python
@dataclass(frozen=True)
class Tier:
    name: str
    label: str
    min_score: float = 0.0
    emoji: str | None = None
    css_class: str = ""
    color: str | None = None

@dataclass(frozen=True)
class TierTable:
    name: str
    tiers: tuple[Tier, ...]    # sorted ascending by min_score
    def classify(self, score: float) -> Tier: ...
```

`TierTable.classify(score)` returns the tier with the highest
`min_score` not exceeding `score`, or the lowest tier if `score` is
below every threshold. Duplicate `min_score` thresholds are rejected at
construction with `ValueError`. `make_tier_table(name, iterable)`
accepts any iterable of tiers and sorts/freezes them.

### 9.7 Formatters

`format_iso_date(value)` and `slugify(text)` are pure utilities. They
are domain-agnostic; adapter-specific date-shape parsers (e.g. Sunbiz
`MMDDYYYY`) and adapter-specific business-age calculations stay in the
adapter, not in calliope. `slugify(text, separator=..., max_length=...)`
trims leading and trailing runs of the chosen separator, returns `""`
for `max_length=0`, and rejects negative `max_length` with
`ValueError`. When `max_length` truncation lands inside a separator run,
the trailing non-alphanumeric characters are stripped so the output
ends in an alphanumeric. This preserves `slugify(slugify(x)) ==
slugify(x)` for any separator made entirely of non-alphanumeric
characters (the supported and recommended case). Separators that
contain alphanumeric characters are not idempotent because alphanumerics
inside a separator survive the next pass through the slug logic;
callers should use only non-alphanumeric separators (`-`, `_`, `--`,
etc.).

## 10. Pages

`calliope.pages` ships substrate-shaped page-composition primitives.
Like cards, the cleanroom page generators are heavily DBPR / Florida
domain-coupled, so calliope re-designs the substrate-shaped abstractions
and pushes domain-specific page logic into adapters.

### 10.1 Pagination

```python
@dataclass(frozen=True)
class Pagination:
    page_number: int       # 1-based
    total_pages: int
    items_per_page: int
    total_items: int

@dataclass(frozen=True)
class PaginationPage:
    pagination: Pagination
    items: tuple[T, ...]

def paginate(items: Sequence[T], items_per_page: int) -> Iterator[PaginationPage]: ...
```

`paginate()` is a streaming iterator: render drivers can iterate
without materializing the full site at once. It always emits at least
one page (an empty index page is still a valid page). `Pagination`
exposes `is_first` / `is_last` / `has_previous` / `has_next` /
`previous_page` / `next_page` for nav-link templates. Construction is
strict: `total_pages` must equal
`max(1, ceil(total_items / items_per_page))`.

### 10.2 Hero

```python
@dataclass(frozen=True)
class Hero:
    title: str
    subtitle: str = ""
    background_image: str | None = None
    background_gradient: str | None = None
    cta_label: str | None = None
    cta_href: str | None = None
    cta_class: str = "hero-cta"
```

`render_hero(hero)` emits a `<section class="hero">…</section>`
wrapped in calliope marker comments (`<!-- BLOCK:hero -->` /
`<!-- /BLOCK:hero -->`) so pages that include a hero can validate the
section as a discrete block. Title / subtitle / CTA label are
HTML-escaped via `templates.safe_value`; `cta_href`, `cta_class`, and
the `container_class` render argument are emitted as escaped attribute
text. The CTA renders only when both label and href are set. `Hero`
accepts at most one of `background_image`, `background_gradient`.
Class-list fields accept only ASCII letters, digits, `_`, `-`, and
single spaces between tokens, and reject HTML entity references
matching `&[#a-zA-Z0-9]+;?` at construction. `background_image`
rejects `"`, `'`, `\n`, `\r`, and HTML entity references matching
`&[#a-zA-Z0-9]+;?`; `background_gradient` rejects those characters plus
`;` and the same entity references before render-time so inline CSS
cannot break out of its attribute or append a second declaration after
HTML decoding.

### 10.3 Scoreboard

```python
@dataclass(frozen=True)
class ScoreboardRow:
    label: str
    count: int = 0
    href: str | None = None
    color: str | None = None
    css_class: str = ""

@dataclass(frozen=True)
class Scoreboard:
    title: str
    rows: tuple[ScoreboardRow, ...]
    total_label: str = "TOTAL"
    show_total: bool = True
    container_class: str = "scoreboard"
    @property
    def total(self) -> int: ...
```

`render_scoreboard(scoreboard)` emits a `<section class="scoreboard">…
</section>` block. Rows with `href` set render as `<a>`; rows without
render as `<div>`. `count` is required `>= 0`. `make_scoreboard(title,
iterable)` is a convenience constructor that accepts any iterable.
`href`, `css_class`, and `container_class` are emitted as escaped
attribute text. Class-list fields accept only ASCII letters, digits,
`_`, `-`, and single spaces between tokens, and reject HTML entity
references matching `&[#a-zA-Z0-9]+;?` at construction. `color`
rejects `"`, `'`, `\n`, `\r`, `;`, and HTML entity references matching
`&[#a-zA-Z0-9]+;?` before render-time so inline CSS cannot append
attacker-controlled declarations after HTML decoding.

### 10.4 Narrative

```python
@runtime_checkable
class NarrativeRenderer(Protocol):
    def render(self, signals: Mapping[str, Any]) -> str: ...

class TemplateNarrativeRenderer:
    def __init__(self, environment: Environment, template_name: str): ...
```

The Protocol decouples narrative composition from any specific backend.
`TemplateNarrativeRenderer` ships as the default Jinja2-backed
implementation; AI-driven renderers belong in adapters (calliope ships
no AI client). Rendered output is whitespace-stripped at the boundary.

### 10.5 Canonical block-name tuples

The following tuples are recommended `TemplateMetadata.blocks` values
for common page archetypes. Adapters can define their own; the
canonical tuples make cross-adapter pages consistent for downstream
tooling:

| Tuple | Sequence |
|---|---|
| `INDEX_PAGE_BLOCKS` | head, header, nav, hero, scoreboard, content, footer |
| `LIST_PAGE_BLOCKS` | head, header, nav, filters, list, pagination, footer |
| `DIMENSION_PAGE_BLOCKS` | head, header, nav, how-to-use, stats, signup, news, content, legal, footer |
| `DETAIL_PAGE_BLOCKS` | head, header, nav, summary, details, related, footer |

`DIMENSION_PAGE_BLOCKS` matches the production sequence at
`L1_metagenerator.py:1331-1369` verbatim; calliope keeps that tuple
stable so pages lifted with this sequence validate without custom
metadata.

## 11. Stage map

| Stage | Subpackage | Lift sources |
|---|---|---|
| 1 | `templates` | spec; `aedifex_template.py` (sanitized helpers); production marker fixtures from `L1_metagenerator.py` |
| 2 | `cards` | substrate primitives designed from spec; `card_components.py` family is reference material, not lift source |
| 3 *(this stage)* | `pages` | substrate primitives (pagination, hero, scoreboard, narrative); `L1_landing_generator.py` / `L1_metagenerator.py` / `L1_narrative.py` are reference material — concrete domain page generators stay in adapters |
| 4 | `render` (per-dimension) | 13× `L1_*_generator.py` |
| 5 | `render` (drivers) | `L1_render_parallel.py`, `L1_render_static_pro.py` |
| 6 | `deploy` | `deploy_tiiny.py` |
| 7 | tag `calliope v0.1.0` | — |

See `docs/LIFT_PATTERN.md` for the per-file lift methodology.

## 12. Versioning

- **Major:** structural change to marker grammar, `TemplateMetadata` shape, or
  subpackage boundaries.
- **Minor:** new `PageTemplate` subclasses, new `bind_data()` features that
  preserve the existing contract.
- **Patch:** bug fixes, documentation, fallback tweaks, internal refactors.

Calliope follows PEP 440. The first stable tag is `v0.1.0`, gated on at least
one working primitive in each of cards, pages, render, deploy.

## 13. Security posture

Calliope is a rendering substrate, not an XSS prevention layer. Its
guarantees about caller-supplied input are scoped:

| Surface | Calliope's behavior | Adapter's responsibility |
|---|---|---|
| Text content (page body, card body, scoreboard labels, hero title/subtitle/CTA label, narrative output) | HTML-escaped via `templates.safe_value` (escapes `<`, `>`, `&`, `"`, `'`). | Pass plain text; calliope handles escaping. |
| `Hero` style-bound fields (`background_image`, `background_gradient`, `cta_class`) | Validated at construction: rejects raw or HTML-entity-encoded `"`, `'`, `\n`, `\r`, `;` (declaration values only). Validators decode via Python's HTML5 entity table (`html.unescape()`), so legacy named entities like `&quot` without `;` are caught. | Sanitize URLs and CSS values from untrusted sources before construction. |
| `Scoreboard.container_class`, `ScoreboardRow.color`, `ScoreboardRow.css_class` | Same construction-time validation as Hero's class/style fields. | Same — sanitize untrusted values. |
| Href fields (`Hero.cta_href`, `ScoreboardRow.href`) | HTML-escaped at render time via `safe_value` (renders inside `href="..."`). **Not** validated at construction; calliope is not a URL validator. | Sanitize URL inputs (scheme, encoding) at the adapter layer. |
| Other attribute sinks (`Pill.css_class`, `Pill.color`, `HeatbarSegment.css_class`/`color`, `templates.shell.html_head` `stylesheets`/`scripts`, `templates.shell.navigation` href values) | **No construction-time validation.** Values are interpolated into HTML/CSS attributes verbatim. | **Sanitize before passing to calliope.** Adapters that render attacker-controlled data through these surfaces must escape and validate at the adapter layer. |

The validators in `calliope.pages._validation` are **defense-in-depth**,
not a complete sanitization layer. Building a complete sanitization
layer for HTML/CSS attribute contexts is a substantial security
project (the WHATWG HTML5 parser has many decoding edge cases) that
belongs in a dedicated library, not the rendering substrate. Adapters
that handle untrusted input should run their own sanitization (e.g.
[bleach](https://bleach.readthedocs.io/), [nh3](https://nh3.readthedocs.io/),
or a domain-specific allow-list) before passing values to calliope.

The validator's `html.unescape()` pass is **single-pass**, which
matches browser behavior: HTML attribute values are decoded once.
Inputs like `&amp;quot;` decode to the literal string `&quot;` and are
emitted as-is — the browser does not recursively decode, so this is
not a bypass.

Calliope's validators on Hero/Scoreboard exist because those
dataclasses encapsulate domain-meaningful semantics (a hero
*background image* is conceptually a URL; a CSS *gradient* is a
declaration value); rejecting obviously-broken inputs at construction
catches typos and trivial misuse without claiming to be a complete
escape barrier.

## 14. What calliope is not

- A general-purpose template engine. Use Jinja2 directly for that.
- A site framework. Calliope renders pages; site structure is the adapter's
  problem.
- A CMS. Calliope is a deterministic build pipeline, not an authoring tool.
- A complete reimplementation of AEDIFEX/ASSG. Calliope adopts the marker
  contract and validation idea; it does not adopt the reference implementation.
- An XSS sanitizer or HTML attribute escape layer. See §13 for the
  security boundary.
