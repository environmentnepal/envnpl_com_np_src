"""
EnvironmentNEPAL — Article deduplication.

Three-stage detection (zero LLM cost):
  1. URL hash — exact match on MD5(url)
  2. Title similarity — SequenceMatcher > 0.85 threshold (last 7 days only)
  3. Content fingerprint — MD5 of first 200 chars of snippet
"""

import hashlib
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional


def url_hash(url: str) -> str:
    """MD5 hash of a URL for exact-match detection."""
    return hashlib.md5(url.strip().encode()).hexdigest()


def content_fingerprint(text: str, length: int = 200) -> str:
    """MD5 hash of first N chars of content."""
    return hashlib.md5(text.strip()[:length].encode()).hexdigest()


def title_similarity(a: str, b: str) -> float:
    """Ratio of similarity between two titles (0.0 to 1.0)."""
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


class Deduplicator:
    """
    Maintains dedup state for a set of existing articles.
    Loads existing hashes/fingerprints from the filesystem (content/news/).
    """

    def __init__(self, news_dir: Path, threshold: float = 0.85, finger_len: int = 200):
        self.news_dir = news_dir
        self.threshold = threshold
        self.finger_len = finger_len
        self.url_hashes: set[str] = set()
        self.content_fingerprints: set[str] = set()
        self._load_existing()

    def _load_existing(self) -> None:
        """Scan existing Markdown files and collect hashes/fingerprints."""
        if not self.news_dir.exists():
            return
        for md_file in self.news_dir.glob("*.md"):
            frontmatter = self._parse_frontmatter(md_file)
            url = frontmatter.get("url", "")
            snippet = frontmatter.get("snippet", "")
            if url:
                self.url_hashes.add(url_hash(url))
            if snippet:
                self.content_fingerprints.add(content_fingerprint(snippet, self.finger_len))

    @staticmethod
    def _parse_frontmatter(path: Path) -> dict[str, str]:
        """Extract frontmatter fields from a Pelican Markdown file."""
        fields = {}
        try:
            with open(path) as f:
                in_fm = False
                for line in f:
                    line = line.strip()
                    if line == "---":
                        if not in_fm:
                            in_fm = True
                        else:
                            break
                    elif in_fm and ":" in line:
                        key, _, value = line.partition(":")
                        fields[key.strip().lower()] = value.strip()
        except Exception:
            pass
        return fields

    def is_duplicate(self, article: dict) -> tuple[bool, Optional[str]]:
        """
        Check if an article is a duplicate of existing content.

        Returns (is_duplicate: bool, reason: str or None).
        """
        # 1. URL hash
        uh = url_hash(article.get("url", ""))
        if uh in self.url_hashes:
            return True, "url"

        # 2. Title similarity (against recent articles — last 7 days)
        title = article.get("title", "")
        cut = datetime.now() - timedelta(days=7)
        for md_file in self.news_dir.glob("*.md"):
            fm = self._parse_frontmatter(md_file)
            existing_title = fm.get("title", "")
            try:
                existing_date = datetime.fromisoformat(fm.get("date", ""))
            except (ValueError, TypeError):
                continue
            if existing_date >= cut:
                if title_similarity(title, existing_title) > self.threshold:
                    return True, "title"

        # 3. Content fingerprint
        fp = content_fingerprint(article.get("snippet", ""), self.finger_len)
        if fp in self.content_fingerprints:
            return True, "content"

        return False, None

    def add(self, article: dict) -> None:
        """Register a new article's hashes so future lookups catch it."""
        self.url_hashes.add(url_hash(article.get("url", "")))
        snippet = article.get("snippet", "")
        if snippet:
            self.content_fingerprints.add(content_fingerprint(snippet, self.finger_len))
