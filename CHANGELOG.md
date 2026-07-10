# EnvironmentNEPAL — Development Log
## Site: https://environmentnepal.com.np/
## Last updated: 2026-07-10
## Total: 93 articles (79 news + 12 parks + 2 books), 7 pages

---

## Phase Completion

| Phase | Status | Deliverables |
|-------|--------|-------------|
| 0 — Repo | ✓ | LICENSE (MIT), .gitignore, requirements.txt, venv |
| 1 — Theme | ✓ | 7 templates (base, index, article, page, category, archives, featured), style.css |
| 2 — Content | ✓ | 12 national parks (Commons images), 5 static pages |
| 3 — Scraper | ✓ | sources.yaml (8 sources), dedupe.py, scraper.py, fetch_content.py, fetch_images.py |
| 4 — CI/CD | ✓ | GitHub Actions → GitHub Pages on push |
| 5 — Books | ✓ | 2 book reviews, 3-col grid |
| 6 — AQI | ✓ | Client-side AQI dashboard |
| 7 — Podcast | ✓ | 4 placeholder episodes |
| 8 — API/MCP | ⏳ | Post-launch |

---

## Current State

- **79 news articles**: Mongabay (36) + Kathmandu Post (22) + Himalayan Times (14) + Nepalitimes (2) + Ratopati (2) + Featured (3)
- **12 national parks** with Commons images
- **2 book reviews** (Snow Leopard, Environmental Justice in Nepal)
- **7 pages**: about-us, privacy, dmca, contact, advertise, aqi, podcast
- **Live**: https://environmentnepal.com.np/
- **Deploy**: Automatic on push to main

---

## News Sources

| Source | Articles | Method | Status |
|--------|----------|--------|--------|
| Mongabay Nepal | 36 | CSS (`.article--container`) | ✓ Working |
| Kathmandu Post | 22 | Links scraper (`/climate-environment/`) | ✓ Working |
| Himalayan Times | 14 | CSS (`article`) | ✓ Working |
| Nepalitimes | 2 | JSON API (`/api/article/{slug}`) | ✓ Needs more slugs |
| Ratopati English | 2 | CSS (`article.post-card__primary`) | ⚠ Keyword filter needed |
| Rising Nepal | — | CSS | ⚠ Nepal-only |
| Nepalnews | — | CSS | ⚠ Nepal-only |
| MyRepublica | — | JS-rendered | ✗ Needs browser automation |

---

## Features Built

### Homepage
- **Header**: Left-aligned "EnvironmentNEPAL" with nav (Home, News, Parks, Books, Data)
- **Hero**: 1 main article (50%) + 2 sub-articles (25% each) with images
- **Featured Section**: Black full-width section pulling article with `Featured: True`
- **Coverage Grid**: 8 articles in 4×2 grid with images
- **Protected Areas**: 4 random parks in 4-column grid
- **Podcasts**: 4 hardcoded episodes in 4-column grid
- **Footer**: About Us, Privacy, DMCA, Contact, Advertise

### Article Pages
- Full body content (~2000 chars) from source scraping
- Article images from source or Commons
- "Read more at [source] →" links opening in new tab
- Image credits on park pages

### Archives (`/archives.html`)
- Grouped by date, 20 items per page, paginated

### Books (`/category/books.html`)
- 3-column grid with cover thumbnails, title, author, year

### Parks (`/category/parks.html`)
- 3-column grid with Commons images and credits

---

## Scraper Architecture

| Script | Purpose |
|--------|---------|
| `scraper.py` | Main engine — 4 extractors (css, rss, links, nepalitimes_api) |
| `dedupe.py` | URL hash + 85% title similarity + 200-char content fingerprint |
| `sources.yaml` | 8 sources with CSS selectors, keyword mappings, check frequency |
| `fetch_content.py` | Extracts ~2000 chars of article body from source pages |
| `fetch_images.py` | Extracts og:image from article pages |

**Extractor types:**
- `css` — Standard HTML scraping with CSS selectors (Mongabay, Himalayan Times, Ratopati)
- `links` — Flat `<a>` tag list scraping for JS-rendered pages (Kathmandu Post)
- `rss` — XML feed parsing (not currently used)
- `nepalitimes_api` — Per-article JSON API with slug list

**Keyword categories:** climate, wildlife, forestry, water, pollution, disaster, policy
**Default fallback:** "environment" (when no keywords match)
**Date filter:** Articles before 2026-01-01 excluded

---

## File Inventory

### Templates (`themes/environmentnepal/templates/`)
| File | Purpose |
|------|---------|
| `base.html` | Shell: header, nav, footer |
| `index.html` | Homepage with all sections |
| `article.html` | Article detail with read-more links |
| `page.html` | Static pages |
| `category.html` | Parks grid, books grid, news list |
| `archives.html` | Date-grouped, paginated news listing |

### Content
| Directory | Count |
| `content/news/` | 79 |
| `content/parks/` | 12 |
| `content/books/` | 2 |
| `content/pages/` | 7 |

---

## Known Quirks

- **{url} warning**: Pelican tries to process `{url}` in article body as template tag — harmless
- **Cloudflare cache**: CSS changes may lag. Bump `?v=N` in base.html if needed
- **Geo-restricted sources**: Rising Nepal, Nepalnews, OnlineKhabar accessible only from Nepal
- **Himalayan Times images**: CDN serves tiny thumbnails (w=30) — scraper now extracts direct URLs
- **MyRepublica**: Fully JS-rendered — needs Puppeteer/Playwright or manual slug collection
- **Nepalitimes slugs**: Stored in `scripts/nepalitimes_slugs.json` — manually add new article slugs
