"""
AI Newspaper Agent — v1
Fetches papers from arXiv RSS + Hugging Face, scores them,
summarizes the best ones, and renders a daily HTML newspaper.

Run:  python src/agent.py
"""

import json
from datetime import date
from anthropic import Anthropic
from fetcher import fetch_all_papers
from renderer import render_newspaper
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv()  # load .env file for API keys, etc.

TOPICS_OF_INTEREST = [
    "large language models",
    "model training and evaluation",
    "reasoning and planning",
    "multimodal models",
    "reinforcement learning from human feedback",
    "AI safety and alignment",
    "agents and tool use",
    "efficient inference",
]

MAX_PAPERS_TO_SCORE = 40   # how many raw papers to send to Claude for scoring
TOP_N_FOR_DIGEST    = 8    # how many make the final newspaper

# ── Agent ─────────────────────────────────────────────────────────────────────

client = Anthropic()

def score_and_select(papers: list[dict]) -> list[dict]:
    """
    Ask Claude to score each paper 1-10 for relevance + novelty,
    then return the top N as structured JSON.
    """
    paper_list = "\n".join(
        f"[{i}] {p['title']} — {p['summary'][:200]}..."
        for i, p in enumerate(papers)
    )

    prompt = f"""You are a senior AI researcher curating a daily digest.

Today's topics of interest:
{chr(10).join(f"- {t}" for t in TOPICS_OF_INTEREST)}

Rate each paper below from 1-10 on:
  - relevance (does it touch our topics?)
  - novelty   (is this a new idea / result, not a survey or minor tweak?)

Return ONLY a JSON array — no markdown, no explanation — like:
[{{"index": 0, "relevance": 8, "novelty": 7}}, ...]

Papers:
{paper_list}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    scores = json.loads(text)

    # Combine score, attach to paper, sort
    for s in scores:
        papers[s["index"]]["score"] = s["relevance"] + s["novelty"]

    ranked = sorted(papers, key=lambda p: p.get("score", 0), reverse=True)
    return ranked[:TOP_N_FOR_DIGEST]


def summarize_paper(paper: dict) -> str:
    """One-paragraph plain-English summary for a non-specialist."""
    prompt = f"""Summarize this AI paper in 3-4 sentences for a technically literate
but non-specialist reader. Be concrete about what's new and why it matters.
Do NOT use bullet points. Write flowing prose.

Title: {paper['title']}
Abstract: {paper['summary']}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def write_headline_and_blurb(paper: dict, summary: str) -> dict:
    """Generate a punchy newspaper-style headline + one-line blurb."""
    prompt = f"""Given this AI paper and its summary, write:
1. A punchy newspaper headline (max 10 words, no jargon)
2. A one-line subheadline / blurb (max 20 words)

Return ONLY JSON: {{"headline": "...", "blurb": "..."}}

Title: {paper['title']}
Summary: {summary}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)

# '{
#     "model": "claude-sonnet-4-6",
#     "max_tokens": 1024,
#     "messages": [
#         {"role": "user", "content": "Hello, world"}
#     ]
# }'


def write_editor_note(top_papers: list[dict]) -> str:
    """A short 'Editor's Note' tying together the day's themes."""
    titles = "\n".join(f"- {p['title']}" for p in top_papers)
    prompt = f"""You are the editor of an AI research newspaper.
Write a 2-sentence 'Editor's Note' that identifies the big theme(s) connecting
today's top papers. Conversational, intelligent, no buzzwords.

Today's papers:
{titles}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run():
    print("📡 Fetching papers...")
    raw_papers = fetch_all_papers()
    print(f"   Found {len(raw_papers)} papers total")

    print("🧠 Scoring & selecting top papers...")
    pool = raw_papers[:MAX_PAPERS_TO_SCORE]   # cap to save tokens
    top_papers = score_and_select(pool)
    print(f"   Selected {len(top_papers)} for the digest")

    print("✍️  Summarizing & writing headlines...")
    articles = []
    for paper in top_papers:
        summary  = summarize_paper(paper)
        copy     = write_headline_and_blurb(paper, summary)
        articles.append({
            **paper,
            "summary_prose": summary,
            "headline":      copy["headline"],
            "blurb":         copy["blurb"],
        })
        print(f"   ✓ {copy['headline']}")

    print("🗞️  Writing editor's note...")
    editor_note = write_editor_note(top_papers)

    print("🎨 Rendering newspaper...")
    output_path = render_newspaper(articles, editor_note, date.today())
    print(f"\n✅ Done! Open: {output_path}")


if __name__ == "__main__":
    run()
