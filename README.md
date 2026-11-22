# AI-Powered Restaurant Recommendation System

Zomato-inspired restaurant recommendations: **structured filtering + LLM ranking/explanations**.

## Docs

- [Problem statement](Docs/problemStatement.md)
- [Architecture](Docs/architecture.md)
- [Implementation plan](Docs/implementation-plan.md)
- [Edge cases](Docs/edge-case.md)

## Requirements

- **Python 3.10+** (3.12 recommended)
- An LLM API key (needed from Phase 3 onward)

## Phase 0 setup

```powershell
cd c:\FirstProjectAi

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure secrets (do not commit .env)
copy .env.example .env
```

Verify the skeleton imports:

```powershell
python -c "import src; print(src.__version__)"
pytest tests/test_imports.py -q
```

## Project layout

```text
FirstProjectAi/
├── Docs/                 # Product & engineering docs
├── data/
│   ├── raw/              # Optional HF dataset cache
│   └── processed/        # Cleaned restaurant store (Phase 1)
├── src/
│   ├── data/             # Ingest + store
│   ├── preferences/      # Preference schema
│   ├── filtering/        # Hard filters
│   ├── llm/              # Prompt, client, parser
│   ├── recommend/        # Orchestration engine
│   ├── api/              # FastAPI routes (Phase 4)
│   └── ui/               # Streamlit UI (Phase 5)
├── tests/
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## Phase 1 — ingest the Zomato dataset

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.data.ingest
```

This downloads [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) into `data/raw/`, cleans it, and writes `data/processed/restaurants.sqlite`.

Quick query demo (city + cuisine, no LLM):

```powershell
python -c "from src.data.store import sample_by_city_cuisine; print(sample_by_city_cuisine('Bangalore', 'Italian', limit=5)[['name','location_raw','rating','cost','budget_band','cuisines_raw']])"
```

## Phase 2 — preferences + hard filtering

```powershell
python -c "from src.filtering import get_candidates; r=get_candidates({'location':'Bangalore','budget':'medium','cuisine':'Italian','min_rating':4.0,'additional_preferences':'family-friendly'}); print('matches', r.match_count, 'returned', len(r.candidates)); print(r.candidates[['name','location_raw','rating','cost','budget_band','cuisines_raw']])"
```

Hard filters: location (city or area), cuisine (any-match tokens), budget band, min rating. Soft `additional_preferences` are validated/truncated but not applied until the LLM phase.

## Phase 3 — Groq LLM ranking + explanations

1. Copy `.env.example` → `.env` and set your Groq key:

```powershell
copy .env.example .env
# Edit .env and set GROQ_API_KEY=...
```

2. Run a recommendation (hard filter → Groq rank/explain):

```powershell
python -c "from src.recommend import recommend; import json; print(json.dumps(recommend({'location':'Bangalore','budget':'medium','cuisine':'Italian','min_rating':4.0,'additional_preferences':'family-friendly'}), indent=2, default=str))"
```

Default model: `openai/gpt-oss-20b` via `https://api.groq.com/openai/v1` (override with `LLM_MODEL`). If the key is missing or Groq fails, the engine falls back to rating-sorted candidates with `meta.used_fallback=true`.

## Phase 4 — API

Start the FastAPI server:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn src.api.routes:app --reload --host 127.0.0.1 --port 8000
```

Then call:

```powershell
curl -X POST http://127.0.0.1:8000/recommend -H "Content-Type: application/json" -d "{\"location\":\"Bangalore\",\"budget\":\"medium\",\"cuisine\":\"Italian\",\"min_rating\":4.0,\"additional_preferences\":\"family-friendly\"}"
```

Or use the CLI entrypoint:

```powershell
python -m src.recommend
python -m src.recommend "{\"location\":\"BTM\",\"budget\":\"low\",\"cuisine\":\"Chinese\",\"min_rating\":4.0}"
```

Open interactive docs at `http://127.0.0.1:8000/docs`.

## Phase 5 — UI

Run the Streamlit preference form (calls the same `recommend()` engine as the API/CLI):

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run src/ui/app.py
```

Enter location, budget, cuisine, minimum rating, and optional soft preferences, then submit. Results show name, cuisine, rating, cost, and the AI explanation. Empty matches and LLM fallback are surfaced in the UI.

Requires Phase 1 ingest (`data/processed/restaurants.sqlite`). Without a Groq key, ranking still works via the rating-sorted fallback.

## Later phases (preview)

| Phase | Command / outcome (once implemented) |
|---|---|
| **6 – Harden** | Full tests, fallbacks, polished README |

## Environment variables

See [`.env.example`](.env.example) for `LLM_API_KEY`, model settings, candidate cap, and processed data path.

## Status

**Phase 5 complete** — Streamlit UI at `src/ui/app.py` demos the full preference → filter → LLM → results flow. Next: Phase 6 (hardening).
