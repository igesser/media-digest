"""
editor.py — the AI EDITOR (the heart of the project).

Sends every collected article to Claude and asks it to behave like Igor's
personal media editor: remove duplicates, rank, pick the best, and for each
winner write a TLDR, a freshness mark, a language tag, and a suggested angle
for Igor's own writing.

The key idea: we don't just ask for text — we force Claude's answer into a
fixed JSON "shape" (SCHEMA) so we always get clean, predictable data back.
"""
import json
import anthropic
from config import MODEL, DIGEST_SIZE, INTERESTS, TOPICS, TOPIC_TAGS, PRIORITIES

# A readable map of Igor's topics → their detailed tags, fed to the editor below.
TOPIC_MAP_TEXT = "\n".join(
    f"- {topic}: {', '.join(tags)}" for topic, tags in TOPIC_TAGS.items()
)

# The exact shape every digest item must have. Claude is constrained to this.
SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title":     {"type": "string"},
                    "tldr":      {"type": "string"},
                    "url":       {"type": "string"},
                    "source":    {"type": "string"},
                    "language":  {"type": "string", "enum": ["en", "ru", "other"]},
                    "fresh":     {"type": "boolean"},
                    "why_fresh": {"type": "string"},
                    "angle":     {"type": "string"},
                    "score":     {"type": "integer"},
                    "topic":     {"type": "string", "enum": TOPICS},
                    "tags":      {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "tldr", "url", "source", "language",
                             "fresh", "why_fresh", "angle", "score", "topic", "tags"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

# The editor's "job description". This is where the editorial judgment lives.
SYSTEM = f"""You are the personal media editor for Igor, a content strategist.
He wants a daily digest to stay current AND to fuel his own writing.

Igor's interests, organized by topic. Use this BOTH to judge how relevant and
valuable each story is to him AND to label each item:
{TOPIC_MAP_TEXT}

(In one line: {INTERESTS}.)

From the list of articles the user gives you:
1. Remove duplicates and near-duplicates (same story from different outlets — keep the best single one).
2. Drop anything off-topic, thin, or purely promotional.
3. Rank what's left by how interesting and useful it is to Igor.
4. Give EXTRA weight to stories about: {", ".join(PRIORITIES)}.
5. Favour genuinely NEW ideas, trends, and recent stories over evergreen explainers.
6. Return UP TO {DIGEST_SIZE} items — but freshness and quality beat quantity: return fewer (even just 6–8) rather than padding with weak or stale picks.

For each item you return:
- tldr: 1–2 crisp sentences on what it says and why it matters. No fluff.
- fresh: true ONLY if it's a genuinely new idea, trend, or shift — not routine news.
- why_fresh: a short phrase explaining the call (e.g. "new format trend" or "routine update").
- language: the article's language ("en", "ru", or "other").
- angle: one sentence suggesting an angle Igor could write about on his own profile.
- score: 0–100, your overall interest rating for Igor (higher = more valuable).
- topic: exactly ONE of these categories, the closest fit: {", ".join(TOPICS)}.
- tags: 1–3 specific tags in English (even for non-English articles), chosen from that topic's list above. Only use a new tag if nothing there fits.
- title, url, source: copy faithfully from the article. NEVER invent a URL.

Order the items by score, highest first."""


def build_digest(items):
    """Send articles to Claude and return the ranked list of digest items."""
    client = anthropic.Anthropic()  # reads your key from the ANTHROPIC_API_KEY env var

    # Turn the articles into one numbered text block for the model to read.
    article_text = "\n\n".join(
        f"[{i}] SOURCE: {a['source']}\nTITLE: {a['title']}\n"
        f"URL: {a['url']}\nSUMMARY: {a['summary']}"
        for i, a in enumerate(items)
    )

    print("   asking Claude to edit the digest …")
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user",
                   "content": f"Here are today's articles:\n\n{article_text}"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )

    # Because of output_config, the first text block is guaranteed valid JSON.
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)["items"]
