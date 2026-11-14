# EnvironmentNEPAL — Refactor Plan & Stack

> Agreed 2026-11-08 between Claude (Claude Code) and opencode, after a two-round site review.
> Status: **proposed — awaiting owner approval.** Philosophy in `specs/handoff.md` still applies
> (static-first, no backend, no LLM dedupe, summary-only content, migration-safe Markdown).

## 1. Stack

| Layer | Choice | Notes |
|---|---|---|
| Site generator | **Pelican 4.12.0** (pinned), Jinja theme `themes/environmentnepal` | Kept: content is plain Markdown, swapping SSG adds no user value. |
| Python | **3.13** (pinned in CI and local) | |
| Pipeline | New package `pipeline/` (replaces `scripts/`) | Stages: fetch → normalize → dedupe → classify/gate → validate → write. |
| Derived data | **Prebuild, not Pelican plugins** | Pipeline writes derived frontmatter + `data/*.json`; templates only read. Testable, not locked to Pelican. |
| Tests / lint | **pytest** (saved HTML/RSS fixtures per source) + **ruff** | |
| Search | **Pagefind** (pinned version, via `actions/setup-node`) | Runs on `output/` after `pelican`. |
| Sitemap | **pelican-sitemap** (pinned) | Build asserts `output/sitemap.xml` exists; fall back to a script only if it breaks on 4.12. |
| SEO | OG/Twitter meta + JSON-LD `NewsArticle` in `base.html` / `article.html` | Category Atom feeds enabled. |
| AQI | **Open-Meteo Air Quality API**, client-side (keyless, CORS) | Replaces the non-existent `/api/aqi`. Map/label its AQI scale and units correctly and verify coverage for Kathmandu, Pokhara, Bharatpur before shipping. |
| CI | `actions/checkout@v4`, `setup-python@v5`, pip + node cache, `pip install -r requirements.txt` (pinned) | `validate` job (ruff + pytest + `validate_content`) is a `needs:` gate before deploy. |
| Scraping | Local cron (current) **+ same code runnable in a scheduled GitHub Action** | The scraper committed on only 24/39 days since 2026-10-01 → single point of failure. Switching prod to Actions = **owner decision**. |
| Timezone | `TIMEZONE = 'Asia/Kathmandu'` | Was `Europe/Rome`. |

## 2. Content contract (frozen in P0)

Written to `data/CONTRACT.md` in P0 (before any other change). News frontmatter:

```yaml
Title: string            # required, no trailing " - Source" suffix
Date: 2026-09-03T21:03:00+05:45   # required, ISO 8601 with offset, Asia/Kathmandu
Category: climate|wildlife|forestry|water|pollution|disaster|policy|environment  # required, lowercase, one only
Source: string           # required, publisher display name
Source_URL: https://...  # required, absolute canonical URL (no query/fragment tracking)
Slug: kebab-case         # required, unique, stable
Snippet: string         # required key, <=200 chars, never == Title, may be ""
Summary: string          # optional; omitted when == Snippet
Image: https://...       # optional
Image_Credit: string     # optional
Parks: chitwan,bardiya   # derived, comma-separated, from the fixed 12-park slug enum
Cluster_ID: string       # derived, stable hash of normalized title/URL
Cluster_Size: integer    # derived
```

Rules: **no body text after the frontmatter**. `validate_content` rejects bodies, empty `Source_URL`,
`Snippet == Title`, unknown categories/parks, duplicate slugs.

Data files (pipeline-owned, theme reads):
- `data/source_health.json` — per source: last success, last error, items fetched/kept per run.
  A source with **no successful fetch in 48h** is `stale` → scheduled job fails (visible alert).
- `data/clusters.json` — cluster id → member slugs, lead slug.

## 3. Phases

**P0 — Safety & truth (fast).**
- Freeze the contract: create `data/CONTRACT.md` (Claude).
- Strip the 71 full article bodies via `migrate.py --dry-run` report first, apply after review (Claude); move `envnepal_gitactions.md`, `revival-of-envnepal.md` out of `content/news/`.
- (opencode) Make `about-us.md` and `privacy.md` match reality (automated aggregation; Google Analytics is loaded in `base.html` — disclose or remove).
- (opencode) Remove the placeholder podcast page and the `#` social links; hide the "Data" nav item until AQI works.
- (Claude) `pelicanconf.py`: timezone, remove the duplicate `DEFAULT_PAGINATION`.

**P1 — Pipeline refactor.**
- `pipeline/` package + pytest fixtures + ruff.
- `migrate.py` **dry-run report first**, then apply: canonical categories, snippet≠title, URL canonicalization, merge known duplicates.
- Tighter relevance gate for `global: true` sources (e.g. "india" alone is not enough) + negative topic filter.
- `source_health.json` + stale alert; scheduled-Action-capable entrypoint (read-only creds except committing `content/` + `data/`).
- Retire `scripts/trim_articles.sh`, `fetch_content.py`, `fetch_images.py`.
- CI: pins, caches, `validate` gate.

**P2 — Discoverability & data.** OG/JSON-LD, sitemap, category feeds, Pagefind search, Open-Meteo AQI page, dead-CSS cleanup.

**P3 — Make it interesting.** Park ↔ news linking ("Latest news" on each park page, park chip on cards),
"Covered by N outlets" badge, auto weekly digest page, "Trending this week". Auto homepage hero and a
district coverage map are deferred until clustering quality is proven.

## 4. Who does what

| Owner | Scope | Branch / worktree |
|---|---|---|
| **Claude** | `pipeline/`, `migrate.py`, tests, `data/` + CONTRACT, CI workflow | `refactor/pipeline` in `../envnpl-claude` |
| **opencode** | All templates (incl. `index.html`), CSS cleanup, SEO meta, Pagefind UI, AQI page, static pages | `refactor/theme` in `../envnpl-oc` |

Rules:
- Pipeline only emits data; it never edits templates.
- Small PR per phase; **each agent reviews the other's PR before merge**.
- Merge order: P0 → P1 pipeline + CONTRACT before any theme PR uses new fields; `refactor/theme` rebases after each pipeline phase.

## 5. Open decisions for the owner

1. Move production scraping to a scheduled GitHub Action (keep local as fallback)? Recommended: yes.
2. Google Analytics: keep and disclose in `privacy.md`, or remove?
3. Books section: delete, or keep the two reviews and drop the "monthly" claim?
4. Podcast: delete the page entirely, or keep a "coming later" stub?
