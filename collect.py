"""
collect.py — the COLLECTORS.

Reads every feed in config.FEEDS and returns a flat list of raw news items.
Handles normal RSS and Google News feeds (where the real outlet sits in a
separate <source> field and gets appended to the title). No AI here.
"""
import re
import html
import feedparser
from config import FEEDS, ARTICLES_PER_FEED

# Pretend to be a normal browser so feeds don't block us.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def clean(text: str) -> str:
    """Strip HTML tags and extra whitespace from a summary, and keep it short."""
    text = html.unescape(text or "")             # turn &#8217; into ', etc.
    text = re.sub(r"<[^>]+>", " ", text)          # remove HTML tags
    text = re.sub(r"\s+", " ", text).strip()      # collapse whitespace
    return text[:500]                              # cap length to save tokens


def parse_entry(entry, feed_name):
    """Turn one raw feed entry into our tidy item dict."""
    title = (entry.get("title") or "").strip()
    url = entry.get("link", "")

    # Google News puts the real outlet in entry.source and appends " - Outlet"
    # to the title. Use that real outlet as the source and tidy the title.
    outlet = ""
    src = entry.get("source")
    if src:
        outlet = src.get("title", "")
    source = outlet or feed_name
    if outlet and title.endswith(" - " + outlet):
        title = title[: -(len(outlet) + 3)].strip()

    return {"source": source, "title": title, "url": url,
            "summary": clean(entry.get("summary", ""))}


def collect_items():
    """Fetch every feed and return a list of {source, title, url, summary}."""
    items = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed["url"], agent=UA)
        n = 0
        for entry in parsed.entries[:ARTICLES_PER_FEED]:
            item = parse_entry(entry, feed["name"])
            if item["title"] and item["url"]:
                items.append(item)
                n += 1
        print(f"   {feed['name']:34} {n:3} items")
    print(f"   ── collected {len(items)} articles in total.")
    return items
