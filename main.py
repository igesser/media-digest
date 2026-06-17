"""
main.py — run this to produce your digest.

It ties the three pieces together:
    collect articles  →  AI editor ranks & writes  →  print to your screen.

Run it from inside the `digest` folder with:  python main.py
"""
from dotenv import load_dotenv
load_dotenv()  # load ANTHROPIC_API_KEY from your .env file BEFORE we use it

import json                          # noqa: E402
from pathlib import Path             # noqa: E402
from datetime import datetime        # noqa: E402

from collect import collect_items   # noqa: E402  (import after load_dotenv on purpose)
from editor import build_digest     # noqa: E402
from build_page import build_html   # noqa: E402
from history import drop_seen       # noqa: E402
from config import DIGEST_SIZE, FRESH_WINDOW_DAYS  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"


def save(digest):
    """Save the digest to data/latest.json (+ a dated copy) for the web page."""
    DATA_DIR.mkdir(exist_ok=True)
    payload = json.dumps(digest, ensure_ascii=False, indent=2)
    (DATA_DIR / "latest.json").write_text(payload, encoding="utf-8")
    (DATA_DIR / f"digest-{datetime.now():%Y-%m-%d}.json").write_text(payload, encoding="utf-8")


def main():
    print("\n📡 Collecting articles from your sources…")
    items = collect_items()
    if not items:
        print("No articles found — check your feed URLs in config.py.")
        return

    before = len(items)
    items = drop_seen(items, DIGEST_SIZE)
    print(f"🆕 Freshness filter: {before} collected → {len(items)} not shown in the last {FRESH_WINDOW_DAYS} days")

    print("\n🧠 The AI editor is reading and ranking…")
    digest = build_digest(items)

    save(digest)              # store the data (data/latest.json)
    page = build_html()       # render the web page (site/index.html)

    print("\n" + "=" * 72)
    print(f"  YOUR MEDIA DIGEST — {len(digest)} items")
    print("=" * 72 + "\n")

    for i, item in enumerate(digest, 1):
        mark = "✨ FRESH" if item.get("fresh") else "      • "
        lang = item.get("language", "").upper()
        print(f"{i:>2}. {mark}  [{lang}]  {item['title']}   ({item['source']})")
        print(f"     TLDR:  {item['tldr']}")
        print(f"     Angle: {item['angle']}")
        print(f"     Topic: {item.get('topic', '')}   Tags: {', '.join(item.get('tags', []))}")
        print(f"     {item['url']}")
        print()

    print(f"🌐 Web page built → {page}")
    print(f'   See it with:   open "{page}"')


if __name__ == "__main__":
    main()
