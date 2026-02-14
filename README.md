# Export Analytics Platform

A Streamlit-based analytics platform for export buyer intelligence.

## Features

- **Dashboard** — KPI metrics and interactive Plotly charts
- **Intelligence** — Filterable buyer data matrix with entity profiles
- **AI Search** — DeepSeek-powered contact data enrichment
- **Email Center** — Mock email client with SMTP config
- **File Manager** — Upload and manage files
- **Settings** — API key configuration

## Tech Stack

- **App**: Streamlit (multipage)
- **Visualization**: Plotly
- **Data**: Pandas + JSON (4.5 MB buyer dataset)
- **AI**: DeepSeek API via OpenAI SDK
- **Backend**: Supabase (optional)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy .env.example to .env and set your keys (optional)
cp .env.example .env

# 3. Run the app
streamlit run app.py
```

## Configuration

Set these environment variables (via `.env` or Streamlit Cloud secrets):

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | No | Supabase project URL |
| `SUPABASE_KEY` | No | Supabase anon/service key |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key for AI Search |

## Development

```bash
# Lint
ruff check .

# Format
ruff format .

# Run tests
pytest -q
```

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub.
2. Connect your GitHub repository to [Streamlit Cloud](https://streamlit.io/cloud).
3. Set secrets (`SUPABASE_URL`, `SUPABASE_KEY`, `DEEPSEEK_API_KEY`) in the Streamlit Cloud dashboard.
4. The app entry point is `app.py` (auto-detected).
