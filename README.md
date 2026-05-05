# 🗞️ The AI Gazette — Personal AI Research Newspaper

A daily digest agent that fetches new AI papers from arXiv and Hugging Face,
scores them for relevance and novelty using Claude, writes plain-English
summaries, and renders a beautiful newspaper-style HTML page.

## Setup

```bash
# 1. Clone / unzip this project, then:
cd ai-newspaper

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."   # or add to .env
```

## Run

```bash
python src/agent.py
```

Output lands in `output/digest_YYYY-MM-DD.html` — open in any browser.

## Automate (Daily Cron)

```bash
# Run every morning at 7am
crontab -e
# Add this line:
0 7 * * * /path/to/.venv/bin/python /path/to/ai-newspaper/src/agent.py
```

Or use **GitHub Actions** (see `.github/workflows/daily.yml` idea below).

## Customize

Edit `src/agent.py` at the top:

```python
TOPICS_OF_INTEREST = [
    "large language models",
    "your topic here",
    ...
]

MAX_PAPERS_TO_SCORE = 40   # increase for broader coverage (more API cost)
TOP_N_FOR_DIGEST    = 8    # papers that make the final newspaper
```

Add more sources in `src/fetcher.py` — any RSS feed or scrapeable page works.

## Project Structure

```
ai-newspaper/
├── src/
│   ├── agent.py       ← main orchestrator (start here)
│   ├── fetcher.py     ← pulls papers from arXiv & HuggingFace
│   └── renderer.py    ← renders the HTML newspaper
├── output/            ← generated digests land here
├── requirements.txt
└── README.md
```

## Phase 2 Ideas (LangGraph refactor)

- [ ] Model as a proper LangGraph StateGraph (fetch → score → summarize → render)
- [ ] Add a "memory" store so it skips papers it already covered
- [ ] Email the digest (SendGrid / SMTP)
- [ ] Push to a Notion page or Slack channel
- [ ] Add Semantic Scholar as a third source
- [ ] Let you chat with the digest ("show me everything about RLHF today")
