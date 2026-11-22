# Implementation Plan

## AI-Powered Restaurant Recommendation System (Zomato Use Case)

Phase-wise plan for building the system described in [`problemStatement.md`](./problemStatement.md) and [`architecture.md`](./architecture.md).

**Approach:** ship a working slice each phase — data first, then filtering, then LLM ranking, then UI — so each stage is demoable before the next begins.

---

## Phase Overview

| Phase | Focus | Outcome |
|---|---|---|
| **0** | Project setup | Runnable repo skeleton + config |
| **1** | Data ingestion | Cleaned, queryable restaurant dataset |
| **2** | Preferences + filtering | Hard-filtered candidate lists from user input |
| **3** | LLM recommendation engine | Ranked restaurants with explanations |
| **4** | Orchestration + API | End-to-end request/response path |
| **5** | UI / output display | User-facing preference form + results |
| **6** | Hardening + polish | Fallbacks, tests, docs, v1 complete |

---

## Phase 0 — Project Setup

**Goal:** Establish a clean Python project that the rest of the work can plug into.

### Tasks

- Initialize repo layout per architecture (`src/`, `data/`, `tests/`, `Docs/`)
- Add `requirements.txt` (or `pyproject.toml`) with baseline deps: `datasets`, `pandas`, LLM client SDK, API/UI libs as needed
- Add `.env.example` for API keys and model config (no real secrets)
- Add a simple entrypoint stub (`README` with how to run later phases)
- Confirm Python version and virtualenv workflow

### Deliverables

- Project skeleton matching [`architecture.md`](./architecture.md) §5
- Dependency and env templates

### Exit criteria

- Empty modules import cleanly; env vars documented; docs linked from README

---

## Phase 1 — Data Ingestion & Processing

**Goal:** Load the Zomato Hugging Face dataset and produce a processed restaurant store.

**Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

### Tasks

- Implement `src/data/ingest.py` to download/load the dataset
- Inspect columns; map to product fields: name, location, cuisine, cost, rating (+ useful extras)
- Clean nulls / bad ratings / inconsistent cuisine strings
- Normalize location and cuisine for matching
- Derive budget bands (`low` / `medium` / `high`) from cost
- Persist processed data under `data/processed/` (Parquet or SQLite)
- Implement `src/data/store.py` to load and query the processed store
- Add a one-time or CLI ingest command

### Deliverables

- Processed restaurant dataset on disk
- Load + basic query helpers

### Exit criteria

- Can load processed data and print sample rows filtered by city/cuisine without the LLM

---

## Phase 2 — User Preferences & Hard Filtering

**Goal:** Accept structured preferences and return a shortlist of matching restaurants.

### Tasks

- Define preference schema (`location`, `budget`, `cuisine`, `min_rating`, `additional_preferences`)
- Validate and normalize inputs
- Implement filter logic:
  - location match
  - cuisine match (token / contains)
  - rating ≥ minimum
  - budget band match
- Cap candidates to top-N (e.g., by rating) for later LLM use
- Keep `additional_preferences` as pass-through soft text (not hard-filtered yet)
- Unit tests for filter edge cases (no matches, partial cuisine, boundary ratings)

### Deliverables

- `src/preferences/` + `src/filtering/` modules
- Test coverage for hard filters

### Exit criteria

- Given sample preferences, system returns a deterministic candidate list with the right fields

---

## Phase 3 — LLM Integration & Recommendation Engine

**Goal:** Turn filtered candidates into ranked, explained recommendations via an LLM.

### Tasks

- Implement LLM client wrapper (`src/llm/client.py`) behind a provider-agnostic interface
- Design prompt template (`src/llm/prompt.py`):
  - user prefs + candidate list
  - rank + explain instructions
  - JSON-only output contract
  - “do not invent restaurants” rule
- Implement response parser/validator (`src/llm/parser.py`)
- Wire recommendation engine to: build prompt → call LLM → parse JSON
- Add fallback: if LLM/parse fails, return rating-sorted candidates with a generic explanation
- Manual dry-run with a small candidate set and real API key

### Deliverables

- Working LLM rank + explain path
- Structured recommendation objects (name, cuisine, rating, cost, explanation)

### Exit criteria

- For a known preference set, LLM returns valid ranked JSON grounded only in provided candidates

---

## Phase 4 — Orchestration & API

**Goal:** Expose the full pipeline as a single recommend flow (CLI and/or HTTP API).

### Tasks

- Implement `src/recommend/engine.py` orchestration: validate → filter → LLM → map response
- Add metadata to responses (`candidates_considered`, `used_fallback`)
- Optional: FastAPI route `POST /recommend` matching architecture request/response contract
- Error handling for empty filters, bad input, LLM timeouts
- Smoke-test the end-to-end path from preferences to structured output

### Deliverables

- Single entry function / API endpoint for recommendations
- Stable request and response shapes

### Exit criteria

- One command or HTTP call produces top recommendations with explanations end-to-end

---

## Phase 5 — UI & Output Display

**Goal:** Let a user enter preferences and see clear recommendation results.

### Tasks

- Build a simple UI (Streamlit/Gradio or lightweight web form):
  - inputs for location, budget, cuisine, min rating, additional preferences
  - submit → call engine/API
- Render results:
  - restaurant name, cuisine, rating, estimated cost
  - AI explanation per item
  - optional overall summary
- Handle empty results and fallback messaging in the UI
- Basic responsive layout for desktop use

### Deliverables

- Runnable UI app that demos the full product flow

### Exit criteria

- Non-technical user can enter prefs and understand why each restaurant was recommended

---

## Phase 6 — Hardening, Testing & v1 Polish

**Goal:** Make the system reliable enough for a solid v1 demo / handoff.

### Tasks

- Expand tests: ingestion field mapping, filters, parser, fallback path
- Tune prompt for consistency (ranking quality, shorter explanations)
- Cap latency/cost (candidate N, max tokens)
- Logging for filter counts and parse failures (no secrets in logs)
- README: setup, env vars, ingest, run UI/API, example preferences
- Align docs (`problemStatement`, `architecture`, this plan) with what was actually built
- Optional stretch: caching processed data load, simple prompt A/B notes

### Deliverables

- Tested v1 application + usage docs

### Exit criteria

- Fresh clone → install → configure key → ingest → run UI/API → get recommendations successfully

---

## Suggested Build Order (Checklist)

```text
[x] Phase 0  Setup
[x] Phase 1  Ingest + processed store
[x] Phase 2  Preferences + hard filters
[x] Phase 3  LLM prompt / client / parser
[x] Phase 4  Orchestration (+ optional API)
[x] Phase 5  UI
[ ] Phase 6  Tests, fallbacks, README polish
```

---

## Dependencies Between Phases

```text
Phase 0
   └─▶ Phase 1 (data)
          └─▶ Phase 2 (filter)
                 └─▶ Phase 3 (LLM)
                        └─▶ Phase 4 (API / engine)
                               └─▶ Phase 5 (UI)
                                      └─▶ Phase 6 (harden)
```

Phases 4 and 5 can overlap slightly (CLI demo before UI), but Phase 3 should be stable before polishing the interface.

---

## Out of Scope for v1 (Defer)

- Embeddings / semantic search over reviews
- User accounts and history
- Maps / distance ranking
- Multi-provider evaluation harness
- Production deployment (Docker/cloud) unless explicitly required later

---

## Definition of Done (Project v1)

The project is complete when:

1. Zomato data is ingested and filterable locally.
2. User preferences drive hard filters correctly.
3. An LLM ranks shortlisted restaurants and explains each pick.
4. Results show name, cuisine, rating, cost, and explanation in a usable UI (or API + simple client).
5. Failures degrade gracefully via fallback ranking.
6. README enables another developer to run the system from scratch.
