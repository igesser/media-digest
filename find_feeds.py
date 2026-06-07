"""
find_feeds.py — given a list of site URLs, find a working RSS/Atom feed for each.

Run:  python find_feeds.py

For each site it prints the best feed URL it found and how many recent items it
has. Use this whenever you want to add new sources: paste homepage URLs into
SITES below, run it, then copy the working feed URLs into config.py.
"""
import re
import urllib.request
import urllib.parse
import feedparser

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

CANDIDATE_PATHS = ["/feed", "/feed/", "/rss", "/rss/", "/rss.xml",
                   "/feed.xml", "/atom.xml", "/index.xml"]

SITES = [
    "https://www.thestateofbrand.com/",
    "https://mediacat.uk/",
    "https://www.codastory.com/",
    "https://thinktankalert.com/",
    "https://www.itsnicethat.com/",
    "https://www.creativeboom.com/",
    "https://www.setters.media/",
    "https://www.fastcompany.com/",
    "https://www.provokemedia.com/",
    "https://www.prdaily.com/",
    "https://www.axios.com/",
    "https://www.semafor.com/vertical/media",
    "https://spinsucks.com/resources/blog/",
    "https://wadds.substack.com/",
    "https://contently.com/strategist/",
    "https://contentmarketinginstitute.com/latest-news",
    "https://www.marketingdive.com/",
    "https://www.niemanlab.org",
    "https://digiday.com",
    "https://www.theverge.com",
]


def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return ""


def discover_from_html(url):
    """Find <link rel=alternate type=application/rss+xml ...> declarations."""
    page = fetch_html(url)
    found = []
    for tag in re.findall(r"<link[^>]+>", page, re.I):
        if re.search(r"application/(rss|atom)\+xml", tag, re.I):
            m = re.search(r'href=["\']([^"\']+)["\']', tag, re.I)
            if m:
                found.append(urllib.parse.urljoin(url, m.group(1)))
    return found


def working_feed(url):
    try:
        d = feedparser.parse(url, agent=UA)
        return len(d.entries), (d.feed.get("title", "") if d.feed else "")
    except Exception:
        return 0, ""


def find(url):
    base = url.rstrip("/")
    candidates = discover_from_html(url) + [base + p for p in CANDIDATE_PATHS] + [url]
    tried = set()
    for c in candidates:
        if c in tried:
            continue
        tried.add(c)
        n, title = working_feed(c)
        if n >= 3:
            return c, n, title
    return None, 0, ""


def main():
    print("Checking", len(SITES), "sites…\n")
    for url in SITES:
        feed, n, title = find(url)
        if feed:
            print(f"OK    {url}\n        {feed}  ({n} items — {title!r})\n")
        else:
            print(f"FAIL  {url}   (no feed found automatically)\n")

    # Bonus: confirm a Google News keyword feed works (topic-based discovery).
    q = "creator economy"
    gn = ("https://news.google.com/rss/search?q="
          + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en")
    d = feedparser.parse(gn, agent=UA)
    sample = d.entries[0].get("link", "") if d.entries else ""
    print(f"GOOGLE NEWS test ['{q}']: {len(d.entries)} items. sample link:\n    {sample}")


if __name__ == "__main__":
    main()
