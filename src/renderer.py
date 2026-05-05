"""
renderer.py — takes processed articles and renders a beautiful HTML newspaper.
"""

import os
from datetime import date

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

SECTION_LABELS = [
    "LEAD STORY",
    "IN DEPTH",
    "RESEARCH BRIEF",
    "RESEARCH BRIEF",
    "RESEARCH BRIEF",
    "ALSO NOTABLE",
    "ALSO NOTABLE",
    "ALSO NOTABLE",
]

def render_newspaper(articles: list[dict], editor_note: str, today: date) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"digest_{today.isoformat()}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    date_str = today.strftime("%A, %B %-d, %Y").upper()

    article_html = ""
    for i, article in enumerate(articles):
        label   = SECTION_LABELS[i] if i < len(SECTION_LABELS) else "ALSO NOTABLE"
        is_lead = i == 0
        card_class = "card card--lead" if is_lead else ("card card--depth" if i == 1 else "card card--brief")

        article_html += f"""
        <article class="{card_class}">
          <div class="card__label">{label}</div>
          <h2 class="card__headline">{article['headline']}</h2>
          <p class="card__blurb">{article['blurb']}</p>
          <p class="card__body">{article['summary_prose']}</p>
          <div class="card__meta">
            <span class="card__source">{article['source']}</span>
            <a class="card__link" href="{article['url']}" target="_blank">Read paper →</a>
          </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>The AI Gazette — {today.isoformat()}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300;1,8..60,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    /* ── Reset & base ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --ink:        #1a1208;
      --ink-mid:    #3d3020;
      --ink-faint:  #7a6a52;
      --paper:      #f5f0e8;
      --paper-dark: #ede6d4;
      --rule:       #c8b89a;
      --accent:     #8b1a1a;
      --accent-mid: #b32424;
      --col-gap:    2rem;
    }}

    html {{ font-size: 16px; }}

    body {{
      background: var(--paper);
      color: var(--ink);
      font-family: 'Source Serif 4', Georgia, serif;
      font-weight: 300;
      line-height: 1.7;
      min-height: 100vh;
    }}

    /* ── Masthead ── */
    .masthead {{
      border-bottom: 3px double var(--ink);
      padding: 1.5rem 2rem 1rem;
      text-align: center;
      position: relative;
    }}

    .masthead__overline {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      color: var(--ink-faint);
      margin-bottom: 0.4rem;
    }}

    .masthead__title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(2.8rem, 8vw, 6rem);
      font-weight: 900;
      line-height: 0.95;
      letter-spacing: -0.02em;
      color: var(--ink);
    }}

    .masthead__title em {{
      font-style: italic;
      color: var(--accent);
    }}

    .masthead__rule {{
      border: none;
      border-top: 1px solid var(--ink);
      margin: 0.75rem auto;
    }}

    .masthead__meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'DM Mono', monospace;
      font-size: 0.62rem;
      letter-spacing: 0.1em;
      color: var(--ink-faint);
      text-transform: uppercase;
      padding-top: 0.25rem;
    }}

    /* ── Editor note ── */
    .editor-note {{
      border-top: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
      padding: 1rem 2rem;
      background: var(--paper-dark);
      display: flex;
      gap: 1rem;
      align-items: baseline;
    }}

    .editor-note__label {{
      font-family: 'DM Mono', monospace;
      font-size: 0.6rem;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      color: var(--accent);
      white-space: nowrap;
      flex-shrink: 0;
      padding-top: 0.15rem;
    }}

    .editor-note__text {{
      font-style: italic;
      font-size: 0.95rem;
      color: var(--ink-mid);
      line-height: 1.6;
    }}

    /* ── Grid ── */
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 0;
      padding: 0 1.5rem;
      max-width: 1280px;
      margin: 0 auto;
    }}

    /* ── Cards ── */
    .card {{
      padding: 1.5rem;
      border-right: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
    }}

    .card:last-child,
    .card--lead {{ border-right: none; }}

    .card--lead {{
      grid-column: 1 / 8;
      border-right: 1px solid var(--rule);
      padding: 2rem 2rem 2rem 1.5rem;
    }}

    .card--depth {{
      grid-column: 8 / 13;
      padding: 1.5rem;
    }}

    .card--brief {{
      grid-column: span 4;
    }}

    @media (max-width: 900px) {{
      .card--lead, .card--depth, .card--brief {{
        grid-column: 1 / -1;
        border-right: none;
      }}
    }}

    .card__label {{
      font-family: 'DM Mono', monospace;
      font-size: 0.58rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 0.5rem;
    }}

    .card__headline {{
      font-family: 'Playfair Display', Georgia, serif;
      font-weight: 700;
      line-height: 1.2;
      color: var(--ink);
      margin-bottom: 0.5rem;
    }}

    .card--lead   .card__headline {{ font-size: clamp(1.6rem, 3vw, 2.4rem); }}
    .card--depth  .card__headline {{ font-size: 1.3rem; }}
    .card--brief  .card__headline {{ font-size: 1.05rem; }}

    .card__blurb {{
      font-style: italic;
      color: var(--ink-mid);
      font-size: 0.95rem;
      margin-bottom: 0.85rem;
      line-height: 1.5;
    }}

    .card--brief .card__blurb {{ display: none; }}

    .card__body {{
      font-size: 0.925rem;
      line-height: 1.75;
      color: var(--ink-mid);
      margin-bottom: 1rem;
    }}

    .card--brief .card__body {{
      font-size: 0.875rem;
      line-height: 1.65;
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .card__meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--rule);
      padding-top: 0.6rem;
      margin-top: auto;
    }}

    .card__source {{
      font-family: 'DM Mono', monospace;
      font-size: 0.6rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--ink-faint);
    }}

    .card__link {{
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--accent);
      text-decoration: none;
      letter-spacing: 0.05em;
    }}
    .card__link:hover {{ text-decoration: underline; }}

    /* ── Footer ── */
    .footer {{
      margin-top: 3rem;
      border-top: 3px double var(--ink);
      padding: 1rem 2rem;
      text-align: center;
      font-family: 'DM Mono', monospace;
      font-size: 0.6rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--ink-faint);
    }}
  </style>
</head>
<body>

  <header class="masthead">
    <p class="masthead__overline">Your personal research digest</p>
    <h1 class="masthead__title">The <em>AI</em> Gazette</h1>
    <hr class="masthead__rule" />
    <div class="masthead__meta">
      <span>{date_str}</span>
      <span>Vol. 1 · Powered by Claude</span>
      <span>{len(articles)} papers curated today</span>
    </div>
  </header>

  <div class="editor-note">
    <span class="editor-note__label">Editor's Note</span>
    <p class="editor-note__text">{editor_note}</p>
  </div>

  <main class="grid">
    {article_html}
  </main>

  <footer class="footer">
    Generated {today.isoformat()} · Sources: arXiv, Hugging Face Papers · For personal use only
  </footer>

</body>
</html>
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath
