# EnvironmentNEPAL

**Nepal-focused environmental news aggregator and static content site** — live at [environmentnepal.com.np](https://environmentnepal.com.np).

Built with [Pelican](https://blog.getpelican.com/) (Python static site generator). Scrapes headlines from 8 Nepali news sources, deduplicates, and generates a clean static site with news, national parks guides, book reviews, an AQI dashboard, and podcast pages.

## Getting Started

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Local Dev Server

Build the site and preview locally:

```bash
pelican content -o output -s pelicanconf.py && pelican --listen
```

Open http://localhost:8000 in your browser.

## Running the News Scraper

All scraping runs **locally** (not in CI). Scraped articles are written as Markdown files to `content/news/`, then committed and pushed — the CI deploy workflow builds and publishes the static site automatically.

### Dry Run (no files written)

```bash
python scripts/scraper.py --dry
```

Fetches sources, identifies new articles, runs deduplication, and prints what **would** be created — but writes nothing.

### Actual Run

```bash
python scripts/scraper.py
```

Fetches sources, deduplicates, writes new Markdown files to `content/news/`, and updates `.last_run.json`.

### Post-Scrape Enrichment (optional)

After scraping, enrich articles with full body text and images:

```bash
python scripts/fetch_content.py   # Adds ~2000 chars of article body
python scripts/fetch_images.py    # Extracts og:image from source URLs
```

## Deployment

CI auto-deploys on push to `main` — no manual steps needed.

## Project Structure

```
├── content/           # Markdown content (news, parks, books, pages)
├── scripts/           # Scraper engine (runs locally)
│   ├── scraper.py         # Main news ingestion
│   ├── dedupe.py          # 3-stage deduplication
│   ├── fetch_content.py   # Body text enrichment
│   ├── fetch_images.py    # Image enrichment
│   └── sources.yaml       # 8 news source configs
├── themes/            # Pelican templates
├── pelicanconf.py     # Dev config
└── publishconf.py     # Production config
```
