# EnvironmentNEPAL — Development Log

## Site: https://environmentnepal.com.np/
## Last updated: 2026-06-06

---

## Phase Completion

| Phase | Status | What was built |
|-------|--------|----------------|
| 0 | ✓ | LICENSE (MIT), .gitignore, requirements.txt, virtual environment |
| 1 | ✓ | 6 Pelican templates (base, index, article, page, category, archives), style.css |
| 2 | ✓ | 12 national park pages, 5 static pages (about-us, privacy, dmca, contact, advertise) |
| 3 | ✓ | Scraping engine: sources.yaml (7 sources), dedupe.py, scraper.py |
| 4 | ✓ | GitHub Actions deploys to GitHub Pages on push |
| 5 | ✓ | Book of the Month (The Snow Leopard), 3-col books grid |
| 6 | ✓ | AQI Dashboard page with client-side JavaScript |
| 7 | ✓ | Podcast page with 4 hardcoded episodes |
| 8 | ⏳ | Post-launch: API + MCP endpoints |

---

## Features Built (Beyond Original Spec)

These emerged during implementation and are NOT in `specs/handoff.md`:

### Homepage
- **Featured Section** — Black full-width section between hero and coverage. Pulls the article with `Featured: True` in frontmatter. Shows image (left) + title + summary + "Read full article →" link. Currently: "Shadows Over the Sky Caves" (Super El Niño 2026).
- **Protected Areas Section** — 4-column grid below podcasts showing 4 parks with Commons images, titles, establishment years. Links to `/category/parks.html`.
- **Article images on cards** — Hero and coverage cards show background images extracted from source article `og:image` meta tags.

### Article Pages
- **Full article body** — Each news article has ~2000 chars of content fetched from the original source (via `scripts/fetch_content.py`).
- **Article images** — Extracted from source `og:image` metadata (via `scripts/fetch_images.py`). Stored in `Image:` frontmatter.
- **"Read more at [source] →"** — External link at bottom of article pages, opens in new tab.
- **Park image credits** — All 12 parks have Wikimedia Commons images with CC attribution displayed on detail pages.

### Archives (`/archives.html`)
- Articles grouped by date (e.g., "06 June 2026" header → list of articles below)
- Paginated: 20 items per page
- Filters out Parks and Books categories

### Books (`/category/books.html`)
- 3-column grid with book cover thumbnails (200px), title, author, year
- Book detail images constrained to 300px max-width
- Review credit: "Review by EnvironmentNEPAL"

### Navigation
- Home → `/`
- News → `/archives.html` (all articles by date)
- Parks → `/category/parks.html` (3-col grid)
- Books → `/category/books.html` (3-col grid)
- Data → `/pages/aqi.html` (AQI dashboard)

### Technical
- **Source_URL rename** — Frontmatter `URL:` renamed to `Source_URL:` to prevent Pelican from treating external URLs as article permalinks.
- **Cloudflare cache bust** — CSS served with `?v=2` query param.
- **Links extractor** — `scraper.py` has a `links` extractor type for React-rendered sites (Kathmandu Post) that scrape flat `<a>` tag lists.

---

## File Inventory

### Templates (`themes/environmentnepal/templates/`)
| File | Purpose |
|------|---------|
| `base.html` | HTML shell: header (left-aligned), nav, footer |
| `index.html` | Homepage: hero (1+2), featured, coverage grid, podcasts, protected areas |
| `article.html` | News/park/book detail page with read-more links |
| `page.html` | Static pages (about-us, privacy, etc.) |
| `category.html` | Category listings: parks grid, books grid, news list |
| `archives.html` | Paginated, date-grouped article listing |

### Scripts (`scripts/`)
| File | Purpose | Run from |
|------|---------|----------|
| `scraper.py` | Main ingestion engine | Local machine (cron) |
| `dedupe.py` | URL hash + title similarity + fingerprint dedup | Imported by scraper |
| `sources.yaml` | 7 news sources with CSS/RSS selectors | Read by scraper |
| `fetch_content.py` | Extract ~2000 chars from article URLs | One-time or periodic |
| `fetch_images.py` | Extract og:image from source pages | One-time or periodic |
| `podcast_generator.py` | TTS podcast generation (placeholder) | Manual |

### Content
| Directory | Count | Description |
|-----------|-------|-------------|
| `content/news/` | 23 files | Scraped news articles with full content |
| `content/parks/` | 12 files | National park pages with Commons images |
| `content/books/` | 1 file | Monthly book review |
| `content/pages/` | 7 files | about-us, privacy, dmca, contact, advertise, aqi, podcast |

### Config
| File | Purpose |
|------|---------|
| `pelicanconf.py` | Dev config, SITEURL, theme, pagination (20) |
| `publishconf.py` | Production config (same SITEURL, RELATIVE_URLS=False) |
| `.github/workflows/deploy.yml` | GitHub Actions: `pelican content -o output -s publishconf.py` → gh-pages |

---

## Current State

- **35 articles**: 23 news + 12 parks + 1 book
- **7 pages**: about-us, privacy, dmca, contact, advertise, aqi, podcast
- **Live**: https://environmentnepal.com.np/
- **Deploy**: Automatic on push to main (GitHub Actions → GitHub Pages)

## Known Quirks

- **Scraper sources**: Rising Nepal, Nepalnews, OnlineKhabar, Himalayan Times time out from outside Nepal. Only Ratopati English and Kathmandu Post work from foreign IPs. URLs and CSS selectors need verification from within Nepal.
- **Cloudflare cache**: CSS changes may lag. Bump `?v=N` in base.html if styles don't update.
- **Pelican warning**: Some articles have `{url}` in body text which Pelican tries to process as a template tag — harmless.

## Remaining

- Phase 8: API + MCP endpoints (post-launch)
- Scraper cron job (`0 */12 * * *`) on operator's machine
- Source URL/selector tuning from within Nepal
- Replace hardcoded podcast episodes with AI-generated audio
