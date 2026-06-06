# EnvironmentNEPAL - Master Handoff Document

> **Purpose:** This document captures all decisions, architecture, layout specifications, and task lists for EnvironmentNEPAL.
> **Development Log**: See `CHANGELOG.md` for commit-by-commit progress.

> **Project Domain:** environmentnepal.com.np
> **Launch Target:** June 4, 2026 (World Environment Day)
> **License:** MIT
> **Repository:** Will be moved to GitHub (public or private as decided)
> **Migration Path:** GitHub Pages is temporary. Site will move to a VPS with a different stack later. All content is plain Markdown + YAML frontmatter to ensure zero-friction migration to any future SSG or CMS.

---

## 📌 PROJECT PHILOSOPHY (DO NOT CHANGE UNLESS USER APPROVES)

1. **Content Integrity First** – Never republish full articles. Only headlines + 1-2 sentence snippets + source links + attribution.
2. **No Membership** – No sign-up, login, or user accounts. Everything is public and free.
3. **API + MCP Ready** – Build for machine access from day one (developers + AI assistants).
4. **Ethical Scraping** – Respect robots.txt, use delays, identify user-agent, support HTTP 304.
5. **Static First** – Use Pelican + GitHub Pages. No dynamic backend unless absolutely necessary.
6. **Cost Efficient** – No LLM for duplicate detection (use hashing + similarity), cache aggressively, batch operations.

---

## 🧠 ARCHITECTURE DECISIONS (FINAL)

| Component | Choice | Reason |
|-----------|--------|--------|
| **Static Site Generator** | Pelican (Python) | Lightweight, works with GitHub Pages, supports Markdown + metadata |
| **Hosting** | GitHub Pages (temporary) | Free, automated via GitHub Actions, no server management. Will migrate to VPS later. |
| **CI/CD** | GitHub Actions | Builds Pelican site on push to main; deploys HTML to gh-pages branch |
| **Scraping** | Python (requests + BeautifulSoup) | Runs locally on operator's machine every 12 hours (cron). Generates Markdown files, pushes to GitHub. |
| **Database** | None (filesystem) | Pelican reads Markdown files; search can use client-side JS (Pagefind) |
| **Duplicate Detection** | URL hash + title similarity (85% threshold) + content fingerprint (first 200 chars) | Zero LLM cost, fast, accurate enough |
| **Categories** | 7 categories: Climate, Wildlife, Forestry, Water, Pollution, Disaster, Policy | Each article gets one primary category |
| **Podcast** | AI-generated weekly (ElevenLabs or OpenAI TTS) → Upload to Spotify/Apple → Embed on site | Static audio files, hosted on GitHub or archive.org |
| **AQI Dashboard** | Static page with JavaScript fetching from IQAir/OpenWeather API | Live data, no backend rebuild needed |

---

## 🎨 LAYOUT SPECIFICATION (FROM USER + THENEWHUMANITARIAN.ORG INSPIRATION)

**Reference site:** thenewhumanitarian.org (user provided screenshot in conversation)

**User modifications:**
- Logo/title on **left** (not centered like TNH)
- No membership/signup anywhere
- Hero section: **1 main story + 2 sub-stories** (not single story)
- Black background section: **1 featured Event with Register button** (not TNH's standard grid)
- "Current coverage" section: **8 stories in 4×2 grid** on white background
- Podcast section: **4 episodes** with embedded audio players

### Full Layout (Top to Bottom)
┌─────────────────────────────────────────────────────────────┐
│ LEFT-ALIGNED HEADER with nav (Home, News, Parks, Books, Data)│
├─────────────────────────────────────────────────────────────┤
│ HERO: 1 Main story (50% width) + 2 sub-stories (25% each) │
├─────────────────────────────────────────────────────────────┤
│ BLACK BACKGROUND SECTION (full width) │
│ 1 Event feature: image (left) + title + description + │
│ "Register" button (right) │
├─────────────────────────────────────────────────────────────┤
│ CURRENT COVERAGE (white background) │
│ "Current coverage" heading → 8 stories (4 columns x 2 rows) │
├─────────────────────────────────────────────────────────────┤
│ PODCAST SECTION: 4 episodes with audio players │
├─────────────────────────────────────────────────────────────┤
│ FOOTER: About Us, Privacy, DMCA, Contact, Advertise links │
└─────────────────────────────────────────────────────────────┘


### Metadata Line Format (per TNH)
Each story shows: `Category | Type | Date`
Example: `Climate | News | 4 June 2026`

### Color Palette
- Primary green: `#2d6a4f`
- Black background: `#1a1a1a`
- Card hover (on black): `#2a2a2a`
- Text light (on black): `#ffffff`
- Metadata text: `#6b7280`

### Responsive Breakpoints
- Desktop >1200px: 4 columns
- Tablet 768–1199px: 2 columns
- Mobile <768px: 1 column

### Section Details (from sample.png)

**Hero section (1+2):**
- Main card (50%): large image with optional text overlays, then headline + metadata below image
- Sub-cards (25% each, stacked vertically on the right): smaller image + headline + metadata

**Event section (black background, full width):**
- 2-column layout inside the dark section:
  - Left: poster/event image (square aspect, ~1:1)
  - Right: Event title (large), description paragraph (2-3 lines), green "Register" button
- All text on this section is white

**Current coverage section (white background):**
- "Current coverage" heading (large, left-aligned)
- 4×2 grid of story cards
- Each card: image (top, ~3:2 aspect), green category tag overlay or below, headline, metadata line
- "All current coverage →" link at bottom right

**Podcast section (white background):**
- "Latest podcasts" heading (left-aligned)
- 4 episode cards in a row
- Each card: square cover art (with title text overlay on cover), metadata line (category | date), episode title
- "All podcasts →" link at bottom right

---

## 📁 REPOSITORY STRUCTURE (TO CREATE)
environmentnepal/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pelican build & deploy to GitHub Pages
├── .gitignore                  # Python venv, __pycache__, output/, .last_run.json
├── LICENSE                     # MIT
├── content/
│ ├── news/                # Generated by scraper (YYYY-MM-DD-title.md)
│ ├── parks/               # Manual Markdown files (chitwan.md, etc.)
│ ├── books/               # Monthly book (YYYY-MM-book-slug.md)
│ └── pages/               # about-us.md, privacy.md, dmca.md, contact.md, advertise.md
├── themes/
│ └── environmentnepal/
│ ├── templates/
│ │ ├── base.html # Left-aligned header, footer, book banner
│ │ ├── index.html # Hero (1+2), Event section, Current coverage, podcast section
│ │ ├── article.html # Individual news article template
│ │ └── page.html # Static pages (about, etc.)
│ └── static/
│ └── css/
│ └── style.css # Grid, colors, responsive
├── scripts/
│ ├── scraper.py # Main ingestion engine
│ ├── dedupe.py # URL hash + title similarity + fingerprint
│ ├── sources.yaml # List of sources with type, frequency, selectors
│ └── podcast_generator.py # Weekly TTS script (optional, can be separate)
├── pelicanconf.py # Development settings
├── publishconf.py # Production settings (GitHub Pages URL)
├── requirements.txt # pelican[markdown], requests, beautifulsoup4, python-frontmatter, etc.
├── Makefile # Generated by pelican-quickstart
└── README.md # Project overview



---

## 🔧 IMPLEMENTATION TASKS (ORDERED)
### Phase 0: Repository Setup (Do this first)
- [ ] Create `LICENSE` file (MIT)
- [ ] Create `.gitignore`:
  ```
  __pycache__/
  *.pyc
  .venv/
  venv/
  output/
  .last_run.json
  .DS_Store
  ```
- [ ] Create `requirements.txt` with: `pelican[markdown]`, `requests`, `beautifulsoup4`, `python-frontmatter`
- [ ] Create virtual environment and install from `requirements.txt`
- [ ] Test Pelican builds locally: `pelican content -o output -s pelicanconf.py`
- [ ] Push to GitHub and verify GitHub Actions deploy works (even if empty site)
### Phase 1: Custom Theme (Layout)
- [ ] Create `themes/environmentnepal/` folder
- [ ] Build `base.html` with left-aligned header (no membership links)
- [ ] Build `index.html` with:
  - Hero section: 1 main article + 2 sub-articles (use `articles` loop)
  - Black background Event section: poster image (left) + title + description + Register button (right)
  - "Current coverage" section: 8 articles in 4×2 grid (use CSS Grid)
  - Podcast section: hardcoded for now (replace with dynamic later)
- [ ] Build `article.html` and `page.html`
- [ ] Write `style.css` with:
  - Grid system for 4/2/1 columns (current coverage and podcast grids)
  - Black section full width (`width: 100vw; margin-left: calc(-50vw + 50%);`)
  - Typography (Inter font, metadata styling)
- [ ] Configure Pelican to use this theme in `pelicanconf.py` (`THEME = 'themes/environmentnepal'`)

### Phase 2: Static Content (National Parks, Pages)
- [ ] Create `content/parks/` folder
- [ ] For each of 12 national parks, create Markdown file with:
  - Title, date (established year), category, slug
  - Body includes: location, area, fees, best season, wildlife, how to reach
  - Frontmatter image (find CC-licensed or Wikimedia Commons images)
- [ ] Create `content/pages/about-us.md` (full About Us page) with sections:
  - Mission: independent coverage of Nepal's environment
  - What we cover: news aggregation, parks, books, data
  - Editorial principles: Content Integrity, no membership, source attribution
  - Team / contact info
  - Sourcing: list of scraped news sources
- [ ] Create `content/pages/privacy.md`, `dmca.md`, `contact.md`, `advertise.md`
- [ ] Test that all pages appear in navigation (update `base.html` if needed)
- [ ] Update footer in `base.html` with links: About Us (`/about-us.html`), Privacy, DMCA, Contact, Advertise

### Phase 3: News Scraping Engine (Runs locally, not in GitHub Actions)
- [ ] Write `scripts/sources.yaml` with at least 5 sources:
  - The Rising Nepal (dynamic)
  - Nepalnews (dynamic)
  - Mongabay Nepal (semi-static, RSS)
  - OnlineKhabar environment section (dynamic)
  - The Himalayan Times environment (dynamic)
- [ ] Write `scripts/dedupe.py` with:
  - `url_hash = hashlib.md5(url.encode()).hexdigest()`
  - `title_similarity()` using `difflib.SequenceMatcher` (threshold 0.85)
  - `content_fingerprint = hashlib.md5(snippet[:200].encode()).hexdigest()`
- [ ] Write `scripts/scraper.py` that:
  - Reads `sources.yaml`
  - Respects `check_frequency` (compare with last run timestamp stored in `.last_run.json` — local only, gitignored)
  - Fetches each source, extracts articles
  - Runs deduplication against existing articles (scan `content/news/` existing files)
  - For new articles, creates Pelican Markdown file in `content/news/YYYY-MM-DD-title.md`
  - Frontmatter includes: Title, Date, Category, Source, URL, Snippet
- [ ] Test scraper locally: `python scripts/scraper.py` → generates `.md` files
- [ ] Commit and push new `content/news/*.md` files to GitHub
- [ ] **Cron setup (deferred):** Set up 12-hour cron (`0 */12 * * *`) on operator's machine at end of project. Runs scraper, auto-commits, and pushes.
- [ ] **Variable volume is normal:** Some runs produce 0 articles (no environment news in 12h), some produce 10+. Both are expected.
### Phase 4: GitHub Actions (Build & Deploy only)
- [ ] Keep existing `.github/workflows/deploy.yml` (already working)
- [ ] Verify it triggers on push to main and deploys to `gh-pages` branch
- [ ] **No scrape workflow** — scraping runs locally, not in GitHub Actions
- [ ] Enable GitHub Pages in repository settings (Source: GitHub Actions, branch: `gh-pages`)
- [ ] Test: push a content change → site redeploys automatically
### Phase 5: Book of the Month (Static + Monthly Update)
- [ ] Create `content/books/2026-06-snow-leopard.md` (example)
- [ ] Add frontmatter: `Title: The Snow Leopard`, `Author: Peter Matthiessen`, `Date: 2026-06-01`, `Slug: snow-leopard`, `Cover: images/snow-leopard.jpg`
- [ ] Write original review/summary (200-300 words)
- [ ] Modify `base.html` to display book banner:
  - Query most recent book (by date) in `content/books/`
  - Show title, author, cover thumbnail, "Read review →" link
- [ ] Monthly update process: manually add new book Markdown file on 1st of month; old book remains in archive

### Phase 6: AQI Dashboard (Client-Side JavaScript)
- [ ] Create `content/pages/aqi.md` (or `content/data/aqi.md`)
- [ ] Write JavaScript that:
  - Fetches from IQAir API (free tier) or OpenWeather
  - Targets Kathmandu, Pokhara, Bharatpur
  - Displays AQI with color coding
  - Updates every hour (client-side `setInterval`)
- [ ] Ensure API keys are stored in GitHub Secrets (not in code)
- [ ] Add AQI widget to sidebar or as separate page

### Phase 7: Podcast Section (Static + AI Generation)
- [ ] Create `content/pages/podcast.md` (or integrate into homepage)
- [ ] Hardcode 4 episodes initially (placeholder)
- [ ] Write `scripts/podcast_generator.py` (optional, can be run manually weekly):
  - Fetch top 5 news articles from last 7 days
  - Generate script: "Welcome to EnvironmentNEPAL Weekly... Top story: [headline]... [snippet]..."
  - Use ElevenLabs or OpenAI TTS API to generate MP3
  - Save MP3 to `content/podcasts/`
  - Update podcast page Markdown with new episode
- [ ] For distribution: upload to Spotify for Podcasters (free) and Apple Podcasts
- [ ] Embed audio players using `<audio controls src="...">`

### Phase 8: API + MCP (Future, after launch)
- [ ] Not required for MVP. Can be added later using a separate Fastify server or serverless functions.
- [ ] If needed: implement `/api/news`, `/api/parks`, `/api/aqi` endpoints (could be Cloudflare Workers or GitHub Pages with client-side JSON generation)

---

## 🤖 SCRAPER DETAILS (IMPLEMENTATION NOTES)

### Source Configuration Format (`sources.yaml`)

```yaml
sources:
  - name: "The Rising Nepal"
    url: "https://risingnepaldaily.com/environment"
    type: dynamic
    check_frequency_hours: 12
    extractor: css
    selector: ".news-article"
    fields:
      title: ".title a"
      url: ".title a@href"
      snippet: ".description"
      date: ".date"
    category_mapping:
      keywords: ["climate", "weather"] → category: climate
      keywords: ["tiger", "rhino", "poaching", "wildlife"] → category: wildlife
      # etc.

## Deduplication
def is_duplicate(new_article, existing_articles):
    # 1. URL hash check
    if md5(new_article.url) in existing_url_hashes:
        return True, "url"
    
    # 2. Title similarity (last 7 days only)
    recent_titles = [a.title for a in existing_articles if a.date > 7 days ago]
    for existing_title in recent_titles:
        if SequenceMatcher(None, new_article.title, existing_title).ratio() > 0.85:
            return True, "title"
    
    # 3. Content fingerprint (first 200 chars)
    new_fingerprint = md5(new_article.snippet[:200])
    if new_fingerprint in existing_fingerprints:
        return True, "content"
    
    return False, None
