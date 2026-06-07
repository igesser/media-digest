"""
config.py — the dials you'll actually touch.

There are THREE kinds of sources:
  1) NATIVE_FEEDS    — sites with their own RSS (best quality, direct links).
  2) BRIDGED_SITES   — sites with NO usable RSS → routed via Google News.
  3) DISCOVERY_QUERIES — Google News topic searches that surface a fresh mix
                         of authors/outlets every day (your "find new voices" idea).
You normally just add/remove lines in those three lists.
"""
import urllib.parse


def google_news(query):
    """Build a Google News RSS feed URL for any search (a topic, or site:domain)."""
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


# 1) NATIVE RSS — sources with their own feed.
NATIVE_FEEDS = [
    {"name": "MediaCat UK",           "url": "https://mediacat.uk/feed/"},
    {"name": "Coda Story",            "url": "https://www.codastory.com/feed/"},
    {"name": "It's Nice That",        "url": "https://feeds2.feedburner.com/itsnicethat/SlXC"},
    {"name": "Creative Boom",         "url": "https://www.creativeboom.com/feed/"},
    {"name": "SETTERS Media",         "url": "https://www.setters.media/post/rss.xml"},
    {"name": "Fast Company",          "url": "https://www.fastcompany.com/rss"},
    {"name": "PR Daily",              "url": "https://www.prdaily.com/feed/"},
    {"name": "Wadds (S. Waddington)", "url": "https://wadds.substack.com/feed"},
    {"name": "Contently Strategist",  "url": "https://contently.com/feed/"},
    {"name": "Marketing Dive",        "url": "https://www.marketingdive.com/feeds/news/"},
    {"name": "Nieman Lab",            "url": "https://www.niemanlab.org/feed/"},
    {"name": "Digiday",               "url": "https://digiday.com/feed/"},
    {"name": "The Verge",             "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Axios",                 "url": "https://api.axios.com/feed/"},
    {"name": "Semafor",               "url": "https://www.semafor.com/rss.xml"},
    {"name": "Spin Sucks",            "url": "https://spinsucks.com/feed/"},
]

# 2) BRIDGED — no usable RSS, so we fetch their stories through Google News.
#    (Upgrade any of these to an RSS.app feed later for fuller text + clean links.)
BRIDGED_SITES = [
    {"name": "PRovoke Media",               "domain": "provokemedia.com"},
    {"name": "Content Marketing Institute", "domain": "contentmarketinginstitute.com"},
    {"name": "The State of Brand",          "domain": "thestateofbrand.com"},
    {"name": "Think Tank Alert",            "domain": "thinktankalert.com"},
]

# 3) DISCOVERY — topic searches that rotate authors/outlets daily. Edit freely.
DISCOVERY_QUERIES = [
    "creator economy",
    "content strategy",
    "brand storytelling",
    "media business model",
]

# The collector reads this combined list (built from the three lists above).
FEEDS = (
    NATIVE_FEEDS
    + [{"name": s["name"], "url": google_news(f"site:{s['domain']}")} for s in BRIDGED_SITES]
    + [{"name": f"Discovery · {q}", "url": google_news(q)} for q in DISCOVERY_QUERIES]
)

# How many recent articles to pull from EACH feed before the editor ranks them.
ARTICLES_PER_FEED = 8

# How many items the final digest should contain (your "top 10–20").
DIGEST_SIZE = 15

# Which Claude model writes the digest.
#   claude-opus-4-8 (best) · claude-sonnet-4-6 (cheaper) · claude-haiku-4-5 (cheapest)
MODEL = "claude-opus-4-8"

# What you care about — the editor uses this to decide what's worth your time.
INTERESTS = (
    "media, content strategy, communications and PR, content creation, "
    "the creator economy, journalism and media business models, branding, "
    "advertising, design, social platforms, and AI's impact on media and content work"
)

# Igor's interest map: 6 topics, each with its detailed tags. The editor uses
# this to (1) judge how relevant a story is to you and (2) label each item with
# ONE topic + a few specific tags. Edit freely — rename topics, add/remove tags.
TOPIC_TAGS = {
    "comms & leadership": [
        "corporate communications", "corporate reputation", "crisis communications",
        "issue management", "stakeholder engagement", "thought leadership",
        "executive positioning", "internal communications", "change management",
        "employee engagement", "employee generated content", "content governance",
        "corporate narrative", "brand purpose",
    ],
    "content strategy & ops": [
        "content strategy", "content architecture", "editorial planning",
        "content pillars", "omnichannel strategy", "content lifecycle",
        "content audits", "content decay", "content repurposing", "modular content",
        "transcreation", "content workflow", "editorial operations",
    ],
    "media & pr": [
        "earned media", "media relations", "public relations strategy", "owned media",
        "corporate publishing", "brand journalism", "paid media", "native advertising",
        "content syndication", "social media strategy", "digital community building",
        "short form video", "b2b podcasting", "newsletter strategy", "audience growth",
    ],
    "storytelling & craft": [
        "business storytelling", "narrative economics", "corporate anthropology",
        "story scouting", "case study methodology", "customer success stories",
        "visual storytelling", "information design", "data visualization",
        "copywriting frameworks", "micro content", "audience psychology",
        "narrative transportation",
    ],
    "ai & tech": [
        "generative ai", "content automation", "large language models",
        "prompt engineering", "synthetic media", "workflow automation",
        "low code automation", "digital asset management", "content personalization",
        "dynamic content", "semantic search optimization",
    ],
    "performance & analytics": [
        "content marketing roi", "communication metrics", "share of voice",
        "sentiment analysis", "media monitoring", "audience insights",
        "behavioral analytics", "content attribution", "engagement modeling",
        "data storytelling", "predictive analytics",
    ],
}

# Derived automatically — no need to edit these.
TOPICS = list(TOPIC_TAGS)                                            # the 6 categories
PREFERRED_TAGS = [t for tags in TOPIC_TAGS.values() for t in tags]  # all tags, flat
