#!/usr/bin/env python3
"""
EnvironmentNEPAL — News ingestion engine.

Reads sources.yaml, fetches articles from configured sources,
deduplicates, and writes Pelican Markdown files to content/news/.

Usage:
    python scripts/scraper.py          # full run
    python scripts/scraper.py --dry    # dry run (prints, no writes)
"""

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup

from dedupe import Deduplicator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
USER_AGENT = (
    "EnvironmentNEPAL/1.0 (news aggregator; environmentnepal.com.np; "
    "respects robots.txt; max 1 req/sec)"
)
REQUEST_DELAY = 1.5  # seconds between requests
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPTS_DIR.parent
SOURCES_YAML = SCRIPTS_DIR / "sources.yaml"
LAST_RUN_FILE = SCRIPTS_DIR / ".last_run.json"
NEWS_DIR = PROJECT_DIR / "content" / "news"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_sources() -> dict:
    with open(SOURCES_YAML) as f:
        return yaml.safe_load(f)


def load_last_run() -> dict[str, str]:
    """Return {source_name: iso_timestamp} for last successful fetch per source."""
    if LAST_RUN_FILE.exists():
        return json.loads(LAST_RUN_FILE.read_text())
    return {}


def save_last_run(timestamps: dict[str, str]) -> None:
    LAST_RUN_FILE.write_text(json.dumps(timestamps, indent=2))


def is_due(source: dict, last_run: dict[str, str]) -> bool:
    """Check if source is due for a fetch based on check_frequency_hours."""
    name = source["name"]
    if name not in last_run:
        return True
    try:
        last = datetime.fromisoformat(last_run[name])
        freq_hours = source.get("check_frequency_hours", 12)
        return (datetime.now(timezone.utc) - last.replace(tzinfo=timezone.utc)).total_seconds() > freq_hours * 3600
    except (ValueError, TypeError):
        return True


def extract_category(title: str, snippet: str, mapping: list[dict]) -> str:
    """Match article title + snippet against keyword rules. Returns category name."""
    text = f"{title} {snippet}".lower()
    for rule in mapping:
        for kw in rule["keywords"]:
            if kw.lower() in text:
                return rule["category"]
    return "climate"  # default fallback


def slugify(title: str) -> str:
    """Convert an article title to a filesystem-safe slug."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:80].strip("-")


def scrape_css(source: dict) -> list[dict]:
    """Scrape articles using CSS selectors (dynamic pages)."""
    url = source["url"]
    print(f"  Fetching: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    selector = source.get("selector", "article")
    fields = source.get("fields", {})

    for element in soup.select(selector):
        title_el = _css_first(element, fields.get("title", "h2 a"))
        url_el = _css_first(element, fields.get("url", "a@href"))
        snippet_el = _css_first(element, fields.get("snippet", "p"))
        date_el = _css_first(element, fields.get("date", "time"))

        title_el = _css_first(element, fields.get("title", "h2 a"))
        url_val = _css_first(element, fields.get("url", "a@href"))
        snippet_el = _css_first(element, fields.get("snippet", "p"))
        date_el = _css_first(element, fields.get("date", "time"))

        # url_val may be string (from @href) or element; handle both
        if isinstance(url_val, str):
            link = url_val
        else:
            link = url_val.get("href", "") if url_val else ""

        title = title_el.get_text(strip=True) if hasattr(title_el, 'get_text') else ""
        snippet = snippet_el.get_text(strip=True) if hasattr(snippet_el, 'get_text') else (snippet_el if isinstance(snippet_el, str) else "")
        raw_date = date_el.get_text(strip=True) if hasattr(date_el, 'get_text') else (date_el if isinstance(date_el, str) else "")
        # Make relative URLs absolute
        if link and not link.startswith("http"):
            link = urljoin(url, link)

        articles.append({
            "title": title,
            "url": link,
            "snippet": snippet[:300],
            "date_raw": raw_date,
            "source_name": source["name"],
        })

    print(f"    Found {len(articles)} articles")
    return articles


def scrape_rss(source: dict) -> list[dict]:
    """Scrape articles from an RSS/Atom feed."""
    url = source["url"]
    print(f"  Fetching RSS: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "xml")

    articles = []
    for item in soup.find_all("item"):
        title = item.find("title")
        link = item.find("link")
        desc = item.find("description")
        pubdate = item.find("pubDate")

        title_text = title.get_text(strip=True) if title else ""
        link_text = link.get_text(strip=True) if link else ""
        desc_text = desc.get_text(strip=True) if desc else ""

        if not title_text or not link_text:
            continue

        # Strip HTML from description
        desc_text = BeautifulSoup(desc_text, "html.parser").get_text(strip=True)

        articles.append({
            "title": title_text,
            "url": link_text,
            "snippet": desc_text[:300],
            "date_raw": pubdate.get_text(strip=True) if pubdate else "",
            "source_name": source["name"],
        })

    print(f"    Found {len(articles)} articles")
    return articles


def scrape_links(source: dict) -> list[dict]:
    """Scrape articles from a page where content is in flat <a> tag lists (React sites)."""
    url = source["url"]
    print(f"  Fetching: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    base = source.get("base_url", "")
    link_pattern = source.get("link_pattern", source["url"])
    articles = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if link_pattern not in href:
            continue
        title = link.get_text(strip=True)
        if len(title) < 10 or href in seen:
            continue
        seen.add(href)

        # Make relative URLs absolute
        if href.startswith("/"):
            href = urljoin(base or url, href)
        elif not href.startswith("http"):
            href = urljoin(url, href)

        # Extract date from URL
        date_match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", href)
        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else datetime.now().strftime("%Y-%m-%d")

        articles.append({
            "title": title,
            "url": href,
            "snippet": title,
            "date_raw": date_str,
            "source_name": source["name"],
        })

    print(f"    Found {len(articles)} articles")
    return articles


def _css_first(element, selector: str):
    """Select first matching element; returns Element, string attr value, or None."""
    if not selector:
        return None
    for sel in [s.strip() for s in selector.split(",")]:
        if "@" in sel and not sel.startswith("@"):
            tag_part, _, attr = sel.partition("@")
            el = element.select_one(tag_part)
            if el and el.has_attr(attr):
                return el[attr]
            if el:
                return el
        else:
            el = element.select_one(sel)
            if el:
                return el
    return None
def create_markdown(article: dict) -> Path:
    """Write a Pelican-compatible Markdown file and return its path."""
    date_str = article.get("date", datetime.now().strftime("%Y-%m-%d"))
    # Normalize date to YYYY-MM-DD
    try:
        dt = datetime.fromisoformat(date_str)
        date_str = dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        date_str = datetime.now().strftime("%Y-%m-%d")

    slug = slugify(article["title"])
    filename = NEWS_DIR / f"{date_str}-{slug}.md"

    frontmatter = f"""\
Title: {article['title']}
Date: {date_str}
Category: {article.get('category', 'climate')}
Source: {article['source_name']}
URL: {article['url']}
Slug: {slug}
Snippet: {article.get('snippet', '')[:200]}
Summary: {article.get('snippet', '')[:200]}
"""

    filename.write_text(frontmatter + "\n")
    return filename


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(dry_run: bool = False) -> None:
    config = load_sources()
    sources = config.get("sources", [])
    last_run = load_last_run()
    dedup = Deduplicator(NEWS_DIR)
    run_timestamps: dict[str, str] = dict(last_run)
    new_count = 0
    now = datetime.now(timezone.utc).isoformat()

    print(f"EnvironmentNEPAL Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(sources)}")
    print(f"  Existing articles in news/: {len(list(NEWS_DIR.glob('*.md'))) if NEWS_DIR.exists() else 0}")
    print()

    for source in sources:
        name = source["name"]
        if not is_due(source, last_run):
            print(f"[SKIP] {name} — not due yet")
            continue

        print(f"[FETCH] {name}")
        try:
            extractor = source.get("extractor", "css")
            if extractor == "rss":
                articles = scrape_rss(source)
            elif extractor == "links":
                articles = scrape_links(source)
            else:
                articles = scrape_css(source)

            time.sleep(REQUEST_DELAY)

            written = 0
            for article in articles:
                # Categorize
                mapping = source.get("category_mapping", [])
                article["category"] = extract_category(
                    article["title"], article["snippet"], mapping
                )

                # Deduplicate
                is_dup, reason = dedup.is_duplicate(article)
                if is_dup:
                    print(f"    [DUP-{reason}] {article['title'][:60]}")
                    continue

                # Create file
                if not dry_run:
                    filepath = create_markdown(article)
                    dedup.add(article)
                    print(f"    [NEW] {filepath.name}")
                else:
                    print(f"    [DRY] {article['title'][:60]} → {article['category']}")
                written += 1

            run_timestamps[name] = now
            new_count += written
            if written:
                print(f"    → {written} new article(s)")
            else:
                print(f"    → no new articles")

        except Exception as e:
            print(f"    [ERROR] {e}")

        time.sleep(REQUEST_DELAY)

    if not dry_run:
        save_last_run(run_timestamps)

    print()
    print(f"Done. {new_count} new articles total.")
    if dry_run:
        print("(Dry run — no files written)")


if __name__ == "__main__":
    dry = "--dry" in sys.argv or "-n" in sys.argv
    main(dry_run=dry)
