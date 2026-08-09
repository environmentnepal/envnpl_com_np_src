# EnvironmentNEPAL

**Nepal-focused environmental news aggregator and static content site** — live at [environmentnepal.com.np](https://environmentnepal.com.np).

Built with [Pelican](https://blog.getpelican.com/) (Python static site generator). The homepage is a Google-News-style feed of environment headlines from Nepali and international outlets. Each card shows a thumbnail, title, source, date, and category tag, and links **directly to the original publisher's article** (opens in a new tab). EnvironmentNEPAL never republishes full articles — only short summaries are stored as metadata.

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

**How it works:**
- Each new article is written as a **summary-only** Markdown file (title, date, category, source, source URL, image, and a short snippet in frontmatter) — no article body.
- Full publish timestamps are parsed so the feed can sort by newest and show live "time ago".
- Sources flagged `global: true` (international outlets) are kept **only** when the story mentions Nepal / South Asia — so the feed stays Nepal-focused even as the source list broadens.
- Env-section sources (Kathmandu Post, The Himalayan Times, Nepalnews, OnlineKhabar, etc.) are pre-filtered by the publisher and are always environment-relevant.
- Off-topic stories (politics, sports, film, crime) are dropped before writing.
- `scripts/fetch_content.py` and `scripts/fetch_images.py` are legacy enrichment scripts — **do not run `fetch_content.py`**, it adds full article bodies, which we no longer store.

## Deployment

CI auto-deploys on push to `main` — no manual steps needed.

## Project Structure

```
├── content/           # Markdown content (news, parks, books, pages)
├── scripts/           # Scraper engine (runs locally)
│   ├── scraper.py         # Main news ingestion
│   ├── dedupe.py          # 3-stage deduplication
│   ├── sources.yaml       # 14 source configs (national + international)
│   └── trim_articles.sh   # Trims each batch to the best articles
├── themes/            # Pelican templates
├── pelicanconf.py     # Dev config
└── publishconf.py     # Production config
```

## News Sources

**National:** Nepali Times, Mongabay Nepal, Ratopati English, Kathmandu Post, The Rising Nepal, Nepalnews, OnlineKhabar, MyRepublica, The Himalayan Times, RecordNepal, The Annapurna Express.

**International (Nepal-tagged):** Dialogue Earth (publishes The Third Pole), The Guardian Environment, Carbon Brief.
