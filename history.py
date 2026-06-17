"""
history.py — the digest's short-term MEMORY.

Each day's digest is saved as data/digest-YYYY-MM-DD.json. Before building a new
one, we look back over the last FRESH_WINDOW_DAYS of those files and cross off any
article we already showed — so every morning is a fresh pack, not yesterday's
top picks again. (Without this, slow-publishing sources and strong evergreen
pieces keep re-winning.)
"""
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from config import FRESH_WINDOW_DAYS

DATA_DIR = Path(__file__).parent / "data"


def normalize(url: str) -> str:
    """A stable key for an article: drop query string, fragment, trailing slash."""
    return (url or "").split("?")[0].split("#")[0].rstrip("/").lower()


def recently_shown_urls():
    """Normalized URLs from the last FRESH_WINDOW_DAYS digests (excluding today)."""
    today = datetime.now().date()
    cutoff = today - timedelta(days=FRESH_WINDOW_DAYS)
    seen = set()
    for f in DATA_DIR.glob("digest-*.json"):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
        if not m:
            continue
        try:
            day = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if day < cutoff or day >= today:   # only previous days, within the window
            continue
        try:
            for item in json.loads(f.read_text(encoding="utf-8")):
                seen.add(normalize(item.get("url", "")))
        except Exception:
            continue
    return seen


def drop_seen(items, min_keep):
    """Remove already-shown items. If too few remain (slow news day), keep
    everything — better a repeat than an empty digest."""
    seen = recently_shown_urls()
    fresh = [it for it in items if normalize(it.get("url", "")) not in seen]
    return fresh if len(fresh) >= min_keep else items
