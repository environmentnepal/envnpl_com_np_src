#!/usr/bin/env python3
"""
Fetch full article content for existing news Markdown files.
Reads content/news/*.md, visits source URLs, extracts body text,
and updates the .md file with article content + "Read more" link.
"""

import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER_AGENT = "EnvironmentNEPAL/1.0 (news aggregator; environmentnepal.com.np)"
NEWS_DIR = Path("content/news")


def fetch_article_body(url: str, source_name: str) -> str:
    """Visit article URL and extract the main body text."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        resp.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    paragraphs = []

    if "ratopati" in source_name.lower():
        # Ratopati: .post-content or main article container
        body = soup.select_one(".post-content, .story-content, main article, article .content")
        if body:
            paragraphs = body.find_all("p")
    elif "kathmandupost" in source_name.lower():
        # Kathmandu Post: article content area
        body = soup.select_one(".story-content, .article-content, .post-content, article .content")
        if body:
            paragraphs = body.find_all("p")
    else:
        # Generic: try common selectors
        for sel in ["article p", ".post-content p", ".story-content p", "main p"]:
            paragraphs = soup.select(sel)
            if len(paragraphs) > 2:
                break

    if not paragraphs:
        return ""

    # Collect paragraphs until we have ~2000 chars or run out
    text_parts = []
    total = 0
    for p in paragraphs:
        txt = p.get_text(strip=True)
        if len(txt) < 20:  # skip short/nav paragraphs
            continue
        text_parts.append(txt)
        total += len(txt)
        if total > 2000:
            break

    return "\n\n".join(text_parts)


def main():
    files = sorted(NEWS_DIR.glob("*.md"))
    print(f"Processing {len(files)} news files...")

    for md_file in files:
        content = md_file.read_text()

        # Skip if already has article body
        if "Read more at" in content:
            continue

        # Extract frontmatter fields
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue

        fm_text = fm_match.group(1)
        url_match = re.search(r"^Source_URL:", fm_text, re.MULTILINE\s*(.+)$", fm_text, re.MULTILINE)
        source_match = re.search(r"^Source:\s*(.+)$", fm_text, re.MULTILINE)

        if not url_match or not source_match:
            continue

        url = url_match.group(1).strip()
        source = source_match.group(1).strip()

        print(f"  Fetching: {md_file.name[:60]}...")
        body = fetch_article_body(url, source)

        if body:
            # Add article body after frontmatter + newline
            updated = re.sub(
                r"(^---\n.*?\n---)",
                r"\1\n\n" + body + f"\n\n*Read more at [{source}]({url})*",
                content,
                count=1,
                flags=re.DOTALL,
            )
            md_file.write_text(updated)
            print(f"    ✓ {len(body)} chars")
        else:
            # Fallback: add read-more link with no body
            updated = re.sub(
                r"(^---\n.*?\n---)",
                r"\1\n\n*Read more at [{source}]({url})*",
                content,
                count=1,
                flags=re.DOTALL,
            )
            md_file.write_text(updated)
            print(f"    ○ no body found, added link only")

        time.sleep(1.5)  # be polite

    print("Done.")


if __name__ == "__main__":
    main()
