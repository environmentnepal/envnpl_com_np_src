#!/usr/bin/env python3
"""
Fetch main image from article source pages and add to frontmatter.
Reads content/news/*.md, visits source URLs, extracts og:image or first large image.
"""

import re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USER_AGENT = "EnvironmentNEPAL/1.0 (aggregator; environmentnepal.com.np)"
NEWS_DIR = Path("content/news")

def fetch_image(url: str) -> str:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
    except:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try og:image first
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"]

    # Try first large image in article
    for img in soup.select("article img, .post-content img, .story-content img"):
        src = img.get("src", "")
        if src and not src.endswith((".svg", ".gif", ".ico")):
            if src.startswith("/"): src = "/" + src.lstrip("/")
            if not src.startswith("http"): continue
            return src

    return ""


def main():
    files = sorted(NEWS_DIR.glob("*.md"))
    updated = 0
    for md_file in files:
        content = md_file.read_text()
        if "Image:" in content:
            continue  # already has image

        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match: continue

        fm = fm_match.group(1)
        url_match = re.search(r"^Source_URL:\s*(.+)$", fm, re.MULTILINE)
        if not url_match: continue

        article_url = url_match.group(1).strip()
        print(f"  {md_file.name[:60]}...", end=" ")
        img = fetch_image(article_url)

        if img:
            new_fm = fm + f"\nImage: {img}"
            updated_content = content.replace(fm, new_fm, 1)
            md_file.write_text(updated_content)
            print(f"✓ {img[:80]}")
            updated += 1
        else:
            print("○ no image found")
        time.sleep(1)

    print(f"\nDone. {updated} articles updated with images.")


if __name__ == "__main__":
    main()
