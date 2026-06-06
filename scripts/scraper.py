#!/usr/bin/env python3
"""EnvironmentNEPAL — News ingestion engine. Usage: python scripts/scraper.py [--dry]"""
import hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
import requests, yaml
from bs4 import BeautifulSoup
from dedupe import Deduplicator

USER_AGENT = "EnvironmentNEPAL/1.0 (aggregator; environmentnepal.com.np)"
REQUEST_DELAY = 1.5
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPTS_DIR.parent
SOURCES_YAML = SCRIPTS_DIR / "sources.yaml"
LAST_RUN_FILE = SCRIPTS_DIR / ".last_run.json"
NEWS_DIR = PROJECT_DIR / "content" / "news"

def load_sources():
    with open(SOURCES_YAML) as f: return yaml.safe_load(f)

def load_last_run():
    if LAST_RUN_FILE.exists(): return json.loads(LAST_RUN_FILE.read_text())
    return {}

def save_last_run(ts):
    LAST_RUN_FILE.write_text(json.dumps(ts, indent=2))

def is_due(source, last_run):
    name = source["name"]
    if name not in last_run: return True
    try:
        last = datetime.fromisoformat(last_run[name])
        freq = source.get("check_frequency_hours", 12)
        return (datetime.now(timezone.utc) - last.replace(tzinfo=timezone.utc)).total_seconds() > freq * 3600
    except: return True

def extract_category(title, snippet, mapping):
    text = f"{title} {snippet}".lower()
    for rule in mapping:
        for kw in rule["keywords"]:
            if kw.lower() in text: return rule["category"]
    return "climate"

def slugify(title):
    s = re.sub(r"[^\w\s-]", "", title.lower().strip())
    s = re.sub(r"[-\s]+", "-", s)
    return s[:80].strip("-")

def _css_first(element, selector):
    if not selector: return None
    for sel in [s.strip() for s in selector.split(",")]:
        if "@" in sel and not sel.startswith("@"):
            tag, _, attr = sel.partition("@")
            el = element.select_one(tag)
            if el and el.has_attr(attr): return el[attr]
            if el: return el
        else:
            el = element.select_one(sel)
            if el: return el
    return None

def scrape_css(source):
    url = source["url"]
    print(f"  Fetching: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    for element in soup.select(source.get("selector", "article")):
        fields = source.get("fields", {})
        url_val = _css_first(element, fields.get("url", "a@href"))
        title_el = _css_first(element, fields.get("title", "h2 a"))
        sn_el = _css_first(element, fields.get("snippet", "p"))
        dt_el = _css_first(element, fields.get("date", "time"))
        link = url_val if isinstance(url_val, str) else (url_val.get("href","") if url_val else "")
        title = title_el.get_text(strip=True) if hasattr(title_el,'get_text') else ""
        snippet = sn_el.get_text(strip=True) if hasattr(sn_el,'get_text') else ""
        raw_date = dt_el.get_text(strip=True) if hasattr(dt_el,'get_text') else ""
        if not title or not link: continue
        if not link.startswith("http"): link = urljoin(url, link)
        articles.append({"title":title,"url":link,"snippet":snippet[:300],"date_raw":raw_date,"source_name":source["name"]})
    print(f"    Found {len(articles)} articles")
    return articles

def scrape_rss(source):
    url = source["url"]
    print(f"  Fetching RSS: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "xml")
    articles = []
    for item in soup.find_all("item"):
        t = item.find("title"); l = item.find("link")
        d = item.find("description"); p = item.find("pubDate")
        title = t.get_text(strip=True) if t else ""
        link = l.get_text(strip=True) if l else ""
        desc = BeautifulSoup(d.get_text(strip=True) if d else "", "html.parser").get_text(strip=True)
        date = p.get_text(strip=True) if p else ""
        if title and link:
            articles.append({"title":title,"url":link,"snippet":desc[:300],"date_raw":date,"source_name":source["name"]})
    print(f"    Found {len(articles)} articles")
    return articles

def scrape_links(source):
    url = source["url"]
    print(f"  Fetching: {url}")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    base = source.get("base_url","")
    pattern = source.get("link_pattern", source["url"])
    articles = []; seen = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if pattern not in href: continue
        title = link.get_text(strip=True)
        if len(title) < 10 or href in seen: continue
        seen.add(href)
        if href.startswith("/"): href = urljoin(base or url, href)
        elif not href.startswith("http"): href = urljoin(url, href)
        dm = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", href)
        ds = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}" if dm else datetime.now().strftime("%Y-%m-%d")
        articles.append({"title":title,"url":href,"snippet":title,"date_raw":ds,"source_name":source["name"]})
    print(f"    Found {len(articles)} articles")
    return articles

def create_markdown(article):
    ds = article.get("date", datetime.now().strftime("%Y-%m-%d"))
    try: ds = datetime.fromisoformat(ds).strftime("%Y-%m-%d")
    except: ds = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(article["title"])
    fm = f"---\nTitle: {article['title']}
Date: {ds}
Category: {article.get('category','climate')}
Source: {article['source_name']}
Source_URL: {article['url']}
Slug: {slug}
Snippet: {article.get('snippet','')[:200]}
Summary: {article.get('snippet','')[:200]}\n---\n"""
    (NEWS_DIR / f"{ds}-{slug}.md").write_text(fm + "\n")
    return f"{ds}-{slug}.md"

def main(dry_run=False):
    config = load_sources()
    sources = config.get("sources", [])
    last_run = load_last_run()
    dedup = Deduplicator(NEWS_DIR)
    run_ts = dict(last_run)
    new_count = 0
    now = datetime.now(timezone.utc).isoformat()
    ne = len(list(NEWS_DIR.glob("*.md"))) if NEWS_DIR.exists() else 0
    print(f"EnvironmentNEPAL Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sources: {len(sources)}, existing articles: {ne}\n")
    for source in sources:
        name = source["name"]
        if not is_due(source, last_run):
            print(f"[SKIP] {name}")
            continue
        print(f"[FETCH] {name}")
        try:
            ext = source.get("extractor","css")
            if ext == "rss": articles = scrape_rss(source)
            elif ext == "links": articles = scrape_links(source)
            else: articles = scrape_css(source)
            time.sleep(REQUEST_DELAY)
            written = 0
            for a in articles:
                a["category"] = extract_category(a["title"], a["snippet"], source.get("category_mapping",[]))
                dup, reason = dedup.is_duplicate(a)
                if dup: print(f"    [DUP-{reason}] {a['title'][:60]}"); continue
                if not dry_run:
                    fname = create_markdown(a); dedup.add(a); print(f"    [NEW] {fname}")
                else: print(f"    [DRY] {a['title'][:60]} -> {a['category']}")
                written += 1
            run_ts[name] = now; new_count += written
            if written: print(f"    → {written} new")
            else: print(f"    → no new")
        except Exception as e: print(f"    [ERROR] {e}")
        time.sleep(REQUEST_DELAY)
    if not dry_run: save_last_run(run_ts)
    print(f"\nDone. {new_count} new articles.")

if __name__ == "__main__":
    main(dry_run="--dry" in sys.argv or "-n" in sys.argv)
