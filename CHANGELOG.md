# EnvironmentNEPAL — Development Log

## Phase Status (2026-06-06)

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| **0 — Repo Setup** | ✓ Done | LICENSE (MIT), .gitignore, requirements.txt, venv, config fix |
| **1 — Custom Theme** | ✓ Done | base.html, index.html, article.html, page.html, category.html, archives.html, style.css |
| **2 — Static Content** | ✓ Done | 12 national parks (Commons images + credits), 5 pages (about-us, privacy, dmca, contact, advertise) |
| **3 — Scraper** | ✓ Done | sources.yaml (7 sources), dedupe.py, scraper.py, fetch_content.py, fetch_images.py |
| **4 — CI/CD** | ✓ Done | deploy.yml (GitHub Actions → GitHub Pages) |
| **5 — Books** | ✓ Done | Snow Leopard review, books category grid (3-col with covers) |
| **6 — AQI Dashboard** | ✓ Done | /pages/aqi.html with client-side JS |
| **7 — Podcast** | ✓ Done | /pages/podcast.html with 4 episodes |
| **8 — API/MCP** | ⏳ Post-launch | Deferred |

---

## Completed Tasks (by commit order)

1. **Phase 0-2** (`refactor phase 1-2`)
   - Created theme with left-aligned header, hero 1+2, event section, 4×2 coverage grid, podcast grid, footer
   - 12 national parks with metadata
   - Static pages with content
   - Moved sample content to news/ with proper categories
   - Layout: left-aligned header, hero (1+2), event section, 4x2 coverage grid, podcast section, footer

2. **CSS Cache Fix** (`fix: bust Cloudflare CSS cache, use publishconf.py for deploy`)
   - Added `?v=2` to CSS link
   - Switched deploy workflow from pelicanconf.py to publishconf.py

3. **Protected Areas** (`feat: Protected Areas section with random parks + Commons images`)
   - Protected Areas section below podcasts (4 parks per row)
   - Wikimedia Commons images for all 12 parks with CC credits
   - image_credit display on park detail pages

4. **Protected Areas Grid Fix** (`fix: Protected Areas grid - remove JS that broke CSS grid layout`)
   - Removed JS shuffle that broke CSS grid

5. **Phase 3 — Scraper** (`feat: Phase 3 - news scraping engine`)
   - scripts/sources.yaml: 7 Nepal news sources
   - scripts/dedupe.py: URL hash + title similarity + content fingerprint
   - scripts/scraper.py: fetch, categorize, dedupe, generate Markdown

6. **Phases 5-7** (`feat: Phases 5-7 — Books, AQI Dashboard, Podcast`)
   - Book of the Month (The Snow Leopard) with banner
   - AQI Dashboard with client-side JS
   - Podcast page with 4 episodes

7. **Real News Content** (`feat: pulled 22 real news articles from Ratopati and Kathmandu Post`)
   - 22 articles from Ratopati English + Kathmandu Post
   - Added 'links' extractor for React sites
   - Fixed @href string handling

8. **Major Fixes** (`fix: nav 404s, article content, book cover, read-more links`)
   - Fixed nav links: Parks, Books, Data → correct Pelican paths
   - Fixed frontmatter `---` delimiters (all 22 files were missing them)
   - Added article body content (~2000 chars via fetch_content.py)
   - "Read more at [source]" links with target="_blank"
   - Book review shows "Review by EnvironmentNEPAL"
   - Book cover from OpenLibrary
   - Rewrote scraper.py clean after corruption

9. **Book Banner Removal + URL Fix** (`fix: news article URLs, remove book banner from homepage`)
   - Renamed URL: → Source_URL: in frontmatter
   - Article internal URLs now correct (not external source URLs)
   - Removed book banner from base.html

10. **Books Grid + Image Size** (`fix: Books page 3-col grid with covers, constrain book detail images`)
    - /category/books.html: 3-col grid with covers
    - Book detail images constrained to 300px

11. **Archives + Images** (`feat: archives pagination, article images, section widths`)
    - Custom archives.html: grouped by date, 20 items/page, pagination
    - fetch_images.py: extracts og:image from source pages
    - 20/22 articles with real images
    - All sections constrained to 1280px

12. **Featured Section** (`feat: featured section replaces event, Super El Niño article`)
    - Renamed event-section → feature-section
    - Featured section pulls article with Featured: True metadata
    - "Shadows Over the Sky Caves" — Super El Niño 2026 deep-dive
    - 2 NOAA climate images (ENSO, temp anomalies)

13. **Featured Image Fix** (`fix: restore Image and Summary fields in featured article`)
    - Restored accidentally dropped Image + Summary fields

---

## Current State

- **35 articles**: 22 news + 12 parks + 1 book
- **7 pages**: about-us, privacy, dmca, contact, advertise, aqi, podcast
- **Live at**: https://environmentnepal.com.np/
- **Scraper**: `python scripts/scraper.py` (run locally from Nepal)

## Remaining Work

- Phase 8: API + MCP (post-launch)
- Scraper cron job setup on operator's machine
- Source URL/selector verification from within Nepal
