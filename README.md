# Igor's AI Media Digest

An AI system that reads many media sources every morning, picks the ~15 most
interesting stories about media / content / the creator economy, and writes a
short digest — with a TLDR, a ✨ freshness mark, a language tag, and a suggested
*angle* for my own writing.

Built as a learning + portfolio project: a real, small, agentic LLM pipeline.

---

## How it works (the architecture)

The system is a little newsroom that runs in a straight line:

```
SOURCES  →  COLLECTORS  →  AI EDITOR  →  OUTPUT
 (RSS)      collect.py     editor.py     main.py
```

| Part | File | What it does |
|------|------|--------------|
| **Config** | `config.py` | The dials: your sources, topics, model, digest size. The one file you edit most. |
| **Collectors** | `collect.py` | Fetches each RSS feed and tidies the raw text. *No AI here.* |
| **AI Editor** | `editor.py` | Sends everything to Claude, which dedupes, ranks, and writes each TLDR + freshness mark + angle. *The heart of the project.* |
| **Runner** | `main.py` | Ties it together and prints the digest. |

### The clever bit: structured output
In `editor.py` we don't just ask Claude for text — we give it a fixed JSON
**schema** and force the answer into that shape. That's why we always get clean,
predictable data (a list of items, each with the same fields) instead of having
to parse free-form writing. This is what makes the AI step *reliable* enough to
build a product on.

---

## Run it

```bash
cd "/Users/igesser/Documents/my s/digest"
source .venv/bin/activate     # turn on this project's isolated Python
python main.py
```

First time only — create your key file:
```bash
cp .env.example .env          # then open .env and paste your real key
```

---

## Customise

- **Add a source:** add a `{"name": ..., "url": ...}` line to `FEEDS` in `config.py`.
- **Change topics:** edit `INTERESTS` in `config.py`.
- **More/fewer items:** change `DIGEST_SIZE`.
- **Cheaper AI:** change `MODEL` to `claude-sonnet-4-6` or `claude-haiku-4-5`.

## Cost
At this scale the AI costs roughly a few cents per run — well under ~$15/month
even when we add many more sources. `claude-opus-4-8` (the default) gives the
best writing; `haiku` is the cheap lever if volume grows a lot.

## Roadmap
- **P1 (now):** RSS → Claude → digest in the terminal ✅
- **P2:** a minimal web page at igesser.com/news
- **P3:** auto-run every morning before 12:00
- **P4:** 👍/👎 feedback so it learns my taste
- **P5:** harder sources (Telegram, newsletters, social)
- **P6:** extras (draft-starter in my voice, morning push, searchable archive, weekly trends)
