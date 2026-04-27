# Calliope Lift Pattern

How cleanroom files become calliope modules. Read alongside
`docs/CALLIOPE-SPEC.md` and the source-of-truth roadmap at
`riskyeats-cleanroom/LEGACY_SRC_RETIREMENT.md`.

---

## Why this exists

Phase 7 lifts ~30 cleanroom files into calliope. Each file has
intra-cleanroom imports (`settings.py`, `column_mappings.py`,
`cerberus_llm_helper.py`), domain-specific strings (jurisdiction-coded
names, brand strings, hardcoded taxonomies), and one or more callers
inside other cleanroom files. Lifting any one file requires deciding,
for every coupling point, whether to *lift along*, *parameterize*, or
*push back into the adapter*.

Stage 1 established the lift pattern by lifting `aedifex_template.py`
and turning the AEDIFEX/ASSG specification into calliope's own contract.
Subsequent stages follow this pattern.

---

## The five-step lift

For each cleanroom file:

### 1. Map the file's surface

```bash
grep -n "^def \|^class " riskyeats-cleanroom/src/<file>.py
grep -rln "from <file>\|import <file>" riskyeats-cleanroom/src/
grep -rln "<file>" riskyeats-cleanroom/  # broader callers
```

Outputs: list of public symbols, list of cleanroom callers.

### 2. Inventory coupling

For each public symbol, list:

- **Internal imports** the function/class uses (`from settings import …`,
  `from column_mappings import …`).
- **Hardcoded domain strings** (brand names, jurisdictions, dimension
  taxonomies, theme tables).
- **Dependencies on cleanroom-only data shapes** (DataFrame column
  names, cleanroom dataclass shapes).
- **External I/O assumptions** (file-system layout, asset paths).

### 3. Decide per coupling point

| Coupling | Resolution |
|---|---|
| Pure-stdlib helpers (path manipulation, slug generation, datetime formatting) | Lift verbatim into `calliope.<subpackage>`. Sanitize only if identifiers reference the cleanroom domain. |
| Hardcoded brand / jurisdiction / dimension strings | Replace with caller-supplied parameters. Calliope ships zero domain literals. |
| Dependencies on cleanroom dataclasses | Replace with `Mapping[str, Any]` or a calliope-defined `Protocol`. The adapter materialises its dataclass-to-mapping bridge. |
| Internal cleanroom imports (`settings`, `column_mappings`, etc.) | The adapter resolves these on the cleanroom side. Calliope accepts pre-resolved values as inputs. |
| Hardcoded asset paths | Caller-supplied `shared_js_path`, `stylesheets`, etc. |
| Hardcoded copy (legal text, attributions) | Caller passes `legal_html`. Calliope ships zero jurisdiction-specific copy. |

### 4. Implement, test, document

- Place the lifted code in the correct subpackage per `CALLIOPE-SPEC.md` §2.
- Add unit tests with **fixtures derived from real production output**
  (cleanroom HTML, real marker comments). Stage 1's
  `tests/conftest.py::PRODUCTION_PAGE_FIXTURE` is the template.
- Update `src/calliope/<subpackage>/__init__.py` to export the new
  surface.
- Update the spec section that covers this subpackage if behaviour
  changed.

### 5. Codex review the diff

Run `codex exec --skip-git-repo-check -c model="gpt-5.4" -c
sandbox_mode="read-only"` with a review prompt that asks for:

- BLOCKER findings (correctness, contract breakage)
- MAJOR findings (architecture, hidden coupling)
- MINOR / NIT (style, naming, comments)

Iterate Codex → fix → re-review until the verdict is `approve`.
Codex is authorized to iterate in-place per the project's
`adversarial-review` policy.

Only commit after `approve`.

---

## Anti-patterns

These come up often when lifting from `riskyeats-cleanroom` and they
have all bitten Stage 1 prep:

- **Lifting domain strings unchanged.** "RiskyEats", "Florida",
  "DBPR", "redalert", "chronic" — every literal that names a
  jurisdiction, brand, or domain dimension must become a parameter.
  Calliope refuses domain literals at the substrate layer.
- **Lifting the AEDIFEX class architecture verbatim.** The reference
  ASSG implementation has known issues that Codex flagged: marker
  grammar that rejects production output, `bind_data()` that drops
  undeclared keys, lexicographic version sort, mutable global
  registry. None of these are lifted; calliope re-implements with the
  contracts intact and the implementation fixed.
- **Treating the AEDIFEX spec as authoritative.** It is a guide, not
  the contract. Calliope's spec at `docs/CALLIOPE-SPEC.md` is the
  contract. Where they disagree, the calliope spec wins.
- **Mixing render-stage concerns into `calliope.templates`.**
  `RenderResult` lives in `calliope.render`; pagination lives in
  `calliope.render`; parallelism lives in `calliope.render`. The
  templates subpackage is the contract surface only.
- **Adopting a global registry.** `TemplateRegistry` is dependency-
  injected per use; tests construct one, adapters construct one, and
  there is no `REGISTRY` singleton.
- **Eager site-wide list materialization.** `bind_data()` operates on
  one page at a time. Render-stage drivers can iterate; the templates
  layer never receives `List[Dict]`.

---

## Reference: the Stage 1 lift in concrete

```text
Source                                        Target
─────────────────────────────────────────     ─────────────────────────────────
aedifex_template.py::get_html_head            calliope.templates.shell.html_head
aedifex_template.py::get_html_header          calliope.templates.shell.html_header
aedifex_template.py::get_navigation           calliope.templates.shell.navigation
aedifex_template.py::get_stats_grid           calliope.templates.shell.stat_grid
aedifex_template.py::get_county_grid          calliope.templates.shell.section_grid
aedifex_template.py::get_html_footer          calliope.templates.shell.html_footer
aedifex_template.py::get_legal_block          calliope.templates.shell.legal_block
aedifex_template.py::get_base_path            calliope.templates.shell.base_path
aedifex_template.py::DIMENSION_THEMES         (dropped — moves to RiskyEats slim)
aedifex_template.py::get_dimension_theme      (dropped — moves to RiskyEats slim)

AEDIFEX-ASSG-Specification.md §5.1            calliope.templates.metadata
AEDIFEX-ASSG-Specification.md §5.2            calliope.templates.base
AEDIFEX-ASSG-Specification.md §6.2-6.3        calliope.templates.base (bind_data, safe_value)
AEDIFEX-ASSG-Specification.md §7              calliope.templates.validation
AEDIFEX-ASSG-Specification.md §8              calliope.templates.extraction
AEDIFEX-ASSG-Specification.md §9.5            calliope.templates.registry
AEDIFEX-ASSG-Specification.md §10.x           (dropped — Stage 5 lifts render drivers from cleanroom directly)
```

---

## When in doubt

- The contract is `docs/CALLIOPE-SPEC.md`.
- The substrate is domain-agnostic. If a calliope module names a
  jurisdiction, a brand, a regulator, a dimension, or a metric, fix it.
- Ship in stages, not megacommits. Each stage should be a Codex-
  reviewable unit (target: ≤ 1500 LOC of new code per stage).
- The adapter holds the domain. Calliope holds the substrate.
