"""
build_page.py — turns the saved digest into a minimal web page.

Reads the latest digest (data/latest.json) and writes ONE self-contained HTML
file (site/index.html), styled to match igesser.com: cream background, DM Sans,
lowercase labels, animated underline links, and an all/en/ru filter toggle.

No server needed — it's a plain file you can open in a browser.
You can also run this file on its own to rebuild the page without calling the AI:
    python build_page.py
"""
import json
import html
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).parent
DATA_FILE = HERE / "data" / "latest.json"
OUT_FILE = HERE / "site" / "index.html"

# The page shell. {{DATE}}, {{COUNT}}, {{ITEMS}} get filled in below.
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>news — igor</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap" rel="stylesheet" />
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root { --bg:#f7f4f0; --text:#1a1a1a; --muted:#999; --line:#e6e1da; --font:'DM Sans',sans-serif; }
  html { background:var(--bg); color:var(--text); font-family:var(--font); font-size:18px; line-height:1.55; -webkit-font-smoothing:antialiased; }
  body { min-height:100vh; padding:48px 56px 80px; max-width:820px; margin:0 auto; position:relative; }

  header { margin-bottom:36px; }
  h1 { font-size:40px; font-weight:400; letter-spacing:-0.5px; line-height:1.15; }
  .sub { color:var(--muted); font-size:12px; letter-spacing:0.08em; text-transform:lowercase; margin-top:10px; }

  .filter { position:absolute; top:48px; right:56px; display:flex; gap:8px; font-size:12px; letter-spacing:0.08em; }
  .filter button { background:none; border:none; cursor:pointer; font:inherit; color:var(--muted); text-transform:lowercase; padding:0; }
  .filter button.active { color:var(--text); }
  .filter span { color:var(--muted); }

  .item { padding:26px 0; border-top:1px solid var(--line); }
  .item:first-of-type { border-top:none; }
  .meta { font-size:12px; color:var(--muted); letter-spacing:0.04em; text-transform:lowercase; margin-bottom:8px; display:flex; gap:12px; flex-wrap:wrap; }
  .meta .fresh { color:var(--text); }
  .title { font-size:21px; font-weight:500; line-height:1.3; }
  .title a { color:var(--text); text-decoration:none; position:relative; }
  .title a::after { content:''; position:absolute; left:0; bottom:0; width:0; height:1px; background:var(--text); transition:width 0.2s ease; }
  .title a:hover::after { width:100%; }
  .tldr { margin-top:8px; }
  .angle { margin-top:8px; color:var(--muted); }
  .angle b { color:var(--text); font-weight:500; }
  .tags { margin-top:12px; display:flex; gap:6px; flex-wrap:wrap; }
  .tag { font-size:11px; letter-spacing:0.04em; color:var(--muted); text-transform:lowercase; border:1px solid var(--line); border-radius:999px; padding:2px 10px; }
  .tag.topic-tag { color:var(--text); border-color:#cfc8be; }

  @media (max-width:700px) { body { padding:36px 24px 60px; } .filter { top:36px; right:24px; } }
</style>
</head>
<body>
  <nav class="filter">
    <button data-f="all" class="active">all</button><span>/</span>
    <button data-f="en">en</button><span>/</span>
    <button data-f="ru">ru</button>
  </nav>

  <header>
    <h1>media digest</h1>
    <div class="sub">{{DATE}} · {{COUNT}} picks</div>
  </header>

  <main>
{{ITEMS}}
  </main>

  <script>
    const buttons = document.querySelectorAll('.filter button');
    const items = document.querySelectorAll('.item');
    buttons.forEach(b => b.addEventListener('click', () => {
      buttons.forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const f = b.dataset.f;
      items.forEach(it => { it.style.display = (f === 'all' || it.dataset.lang === f) ? '' : 'none'; });
    }));
  </script>
</body>
</html>
"""

ITEM = """    <article class="item" data-lang="{lang}">
      <div class="meta"><span>{source}</span>{fresh}<span>{langlabel}</span></div>
      <div class="title"><a href="{url}" target="_blank" rel="noopener">{title}</a></div>
      <p class="tldr">{tldr}</p>
      <p class="angle"><b>angle</b> — {angle}</p>
      <div class="tags">{tags}</div>
    </article>"""


def build_html():
    """Read the latest digest JSON and write site/index.html. Returns the path."""
    digest = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    rows = []
    for it in digest:
        lang = (it.get("language") or "other").lower()
        fresh = '<span class="fresh">✨ fresh</span>' if it.get("fresh") else ""
        topic = it.get("topic", "")
        topic_pill = f'<span class="tag topic-tag">{html.escape(topic)}</span>' if topic else ""
        tags_html = topic_pill + "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in it.get("tags", [])
        )
        rows.append(ITEM.format(
            lang=html.escape(lang),
            source=html.escape(it.get("source", "")),
            fresh=fresh,
            langlabel=html.escape(lang.upper()),
            url=html.escape(it.get("url", "#"), quote=True),
            title=html.escape(it.get("title", "")),
            tldr=html.escape(it.get("tldr", "")),
            angle=html.escape(it.get("angle", "")),
            tags=tags_html,
        ))

    page = (PAGE
            .replace("{{DATE}}", datetime.now().strftime("%d %B %Y").lower())
            .replace("{{COUNT}}", str(len(digest)))
            .replace("{{ITEMS}}", "\n".join(rows)))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(page, encoding="utf-8")
    return OUT_FILE


if __name__ == "__main__":
    path = build_html()
    print(f"Page built → {path}")
