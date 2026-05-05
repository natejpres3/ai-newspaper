"""
fetcher.py — pulls papers from multiple sources into a unified list.

Sources:
  1. arXiv RSS feeds  (cs.AI, cs.LG, cs.CL)
  2. Hugging Face Daily Papers page (scraped)

Each paper is a dict:
  {
    "title":   str,
    "summary": str,      # abstract / description
    "url":     str,
    "source":  str,
    "date":    str,
  }
"""

import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ── arXiv ─────────────────────────────────────────────────────────────────────

ARXIV_FEEDS = [
    ("cs.AI",  "https://rss.arxiv.org/rss/cs.AI"),
    ("cs.LG",  "https://rss.arxiv.org/rss/cs.LG"),
    ("cs.CL",  "https://rss.arxiv.org/rss/cs.CL"),
]

def fetch_arxiv() -> list[dict]:
    papers = []
    for category, url in ARXIV_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            papers.append({
                "title":   entry.get("title", "").replace("\n", " ").strip(),
                "summary": entry.get("summary", "").replace("\n", " ").strip(),
                "url":     entry.get("link", ""),
                "source":  f"arXiv ({category})",
                "date":    entry.get("published", str(datetime.now(timezone.utc).date())),
            })
    print(f"   arXiv: {len(papers)} papers")
    return papers


# ── Hugging Face Daily Papers ──────────────────────────────────────────────────

HF_PAPERS_URL = "https://huggingface.co/papers"

def fetch_huggingface() -> list[dict]:
    try:
        r = httpx.get(HF_PAPERS_URL, timeout=15, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (compatible; ai-newspaper/1.0)"})
        r.raise_for_status()
    except Exception as e:
        print(f"   HuggingFace fetch failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    papers = []

    # Each paper card has an <h3> title and an <a> link
    for card in soup.select("article"):
        title_tag = card.find("h3") or card.find("h2")
        link_tag  = card.find("a", href=True)
        desc_tag  = card.find("p")

        if not title_tag:
            continue

        title   = title_tag.get_text(strip=True)
        url     = link_tag["href"] if link_tag else ""
        if url.startswith("/"):
            url = "https://huggingface.co" + url
        summary = desc_tag.get_text(strip=True) if desc_tag else title

        papers.append({
            "title":   title,
            "summary": summary,
            "url":     url,
            "source":  "Hugging Face Papers",
            "date":    str(datetime.now(timezone.utc).date()),
        })

    print(f"   Hugging Face: {len(papers)} papers")
    return papers


# ── Deduplicate ────────────────────────────────────────────────────────────────

def deduplicate(papers: list[dict]) -> list[dict]:
    seen, result = set(), []
    for p in papers:
        key = p["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result


# ── Public API ─────────────────────────────────────────────────────────────────

def fetch_all_papers() -> list[dict]:
    all_papers = fetch_arxiv() + fetch_huggingface()
    unique     = deduplicate(all_papers)
    print(f"   Total unique: {len(unique)}")
    return unique
