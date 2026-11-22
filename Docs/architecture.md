# Architecture

## AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document defines the detailed architecture for the restaurant recommendation service described in [`problemStatement.md`](./problemStatement.md). The system combines structured restaurant data with an LLM to produce ranked, explained recommendations.

---

## 1. High-Level Overview

The application follows a **filter-then-reason** pipeline:

1. Load and normalize the Zomato dataset once (or on startup / cache refresh).
2. Collect user preferences through a UI or API.
3. Apply deterministic filters on structured fields (location, budget, cuisine, rating).
4. Send the filtered candidate set to an LLM with a carefully designed prompt.
5. Receive ranked recommendations with explanations and render them to the user.

```text
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│ User Input  │────▶│ Filtering Layer  │────▶│ LLM Recommender │────▶│ Output View  │
│ (prefs)     │     │ (structured)     │     │ (rank + explain)│     │ (results UI) │
└─────────────┘     └────────▲─────────┘     └─────────────────┘     └──────────────┘
                             │
                    ┌────────┴─────────┐
                    │ Restaurant Store │
                    │ (preprocessed    │
                    │  Zomato data)    │
                    └──────────────────┘
```

**Design principle:** Use code for exact constraints (location, budget bands, cuisine, min rating). Use the LLM for soft ranking, preference interpretation, and natural-language explanations.

---

## 2. Logical Layers

| Layer | Responsibility |
|---|---|
| **Presentation** | Collect preferences; display ranked restaurants and AI explanations |
| **Application / API** | Validate input, orchestrate filter → prompt → LLM → response mapping |
| **Integration** | Build candidate payloads and prompt templates for the LLM |
| **Recommendation Engine** | Call the LLM; parse ranked results and explanations |
| **Data** | Ingest, clean, store, and query the Zomato dataset |

---

## 3. Component Architecture

### 3.1 Data Ingestion Module

**Source:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) on Hugging Face.

**Responsibilities:**

- Download / load the dataset (Hugging Face `datasets` library or cached local copy)
- Select and normalize fields used by the product:
  - Restaurant name
  - Location / city / area
  - Cuisine(s)
  - Approximate cost / price for two
  - Rating / votes (if available)
  - Optional metadata useful for soft preferences (e.g., type, online order, table booking)
- Clean nulls, normalize cuisine tokens, map cost into budget bands (`low` / `medium` / `high`)
- Persist a processed dataset (CSV/Parquet/SQLite) for fast filtering

**Outputs:** A queryable restaurant table/index used by the filtering layer.

### 3.2 User Preference Module

**Inputs collected from the user:**

| Field | Type | Notes |
|---|---|---|
| `location` | string | City or area (e.g., Bangalore) |
| `budget` | enum | `low`, `medium`, `high` |
| `cuisine` | string / list | e.g., Italian, Chinese |
| `min_rating` | number | Inclusive lower bound |
| `additional_preferences` | free text | Soft constraints for the LLM (family-friendly, quick service, romantic, etc.) |

**Responsibilities:**

- Validate required fields
- Normalize cuisine/location strings for matching
- Keep free-text preferences separate from hard filters

### 3.3 Filtering / Integration Layer

**Hard filters (deterministic):**

- Match location
- Match cuisine (exact or token overlap)
- Enforce minimum rating
- Restrict to budget band using precomputed cost ranges

**Soft preparation for the LLM:**

- Cap candidates (e.g., top N by rating after filter) to control prompt size/cost
- Serialize each candidate into a compact structured record:
  - `name`, `cuisine`, `rating`, `cost`, `location`, optional tags
- Compose a prompt that includes:
  - User preference summary
  - Candidate restaurant list
  - Instructions to rank, explain, and optionally summarize

This layer is the bridge between structured data retrieval and generative reasoning.

### 3.4 Recommendation Engine (LLM)

**Responsibilities:**

- Call the configured LLM provider (API or local model)
- Instruct the model to:
  - Rank restaurants for the given preferences
  - Explain why each pick fits
  - Optionally produce a short overall summary
- Request a **structured response** (JSON) for reliable UI rendering
- Validate/parse the model output; fall back to a default ranking (e.g., by rating) if parsing fails

**Expected LLM output shape:**

```json
{
  "summary": "Short overview of the picks",
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "Example Cafe",
      "cuisine": "Italian",
      "rating": 4.5,
      "estimated_cost": "medium",
      "explanation": "Why this matches the user"
    }
  ]
}
```

### 3.5 Presentation / Output Module

Display for each recommendation:

- Restaurant name
- Cuisine
- Rating
- Estimated cost / budget band
- AI-generated explanation

Optionally show an overall summary and a note when results were truncated or fallback ranking was used.

---

## 4. End-to-End Data Flow

```text
1. Startup / offline job
   Hugging Face dataset
        → clean + normalize
        → budget banding
        → local processed store

2. Request path
   User preferences
        → validate
        → hard filter on processed store
        → select top-N candidates
        → build LLM prompt
        → LLM ranks + explains
        → parse structured response
        → render recommendations
```

**Sequence (request):**

1. Client submits preferences.
2. API validates and normalizes input.
3. Filter service queries the restaurant store.
4. Prompt builder creates the LLM request from candidates + preferences.
5. LLM client returns ranked JSON.
6. Response mapper maps JSON → UI/API DTO.
7. Client renders the recommendation list.

---

## 5. Suggested Project Structure

```text
FirstProjectAi/
├── Docs/
│   ├── problemStatement.md
│   └── architecture.md
├── data/
│   ├── raw/                  # optional local cache of HF dataset
│   └── processed/            # cleaned restaurant records
├── src/
│   ├── data/
│   │   ├── ingest.py         # load HF dataset, clean, persist
│   │   └── store.py          # read/query processed data
│   ├── preferences/
│   │   └── schema.py         # preference models / validation
│   ├── filtering/
│   │   └── filter.py         # hard filters + candidate selection
│   ├── llm/
│   │   ├── prompt.py         # prompt templates
│   │   ├── client.py         # LLM API wrapper
│   │   └── parser.py         # response parsing / validation
│   ├── recommend/
│   │   └── engine.py         # orchestration: filter → LLM → result
│   ├── api/                  # optional FastAPI/Flask routes
│   │   └── routes.py
│   └── ui/                   # optional Streamlit/Gradio/web frontend
│       └── app.py
├── tests/
├── .env.example              # API keys / model config (no secrets committed)
└── requirements.txt
```

Exact framework choices can vary; the module boundaries above should remain stable.

---

## 6. Technology Choices (Recommended Baseline)

| Concern | Recommendation | Rationale |
|---|---|---|
| Language | Python | Strong HF + LLM ecosystem |
| Dataset access | `datasets` (Hugging Face) | Direct load of the specified Zomato dataset |
| Data processing | pandas / polars | Cleaning, filtering, budget banding |
| Processed store | Parquet or SQLite | Fast local queries without a heavy DB |
| API (optional) | FastAPI | Typed request/response models |
| UI (optional) | Streamlit or simple web UI | Fast preference form + results view |
| LLM | Configurable provider (OpenAI-compatible, Gemini, local, etc.) | Keep behind a client interface |
| Config / secrets | Environment variables | API keys never hardcoded |

---

## 7. Prompt Architecture

### Prompt inputs

- Normalized user preferences (hard + soft)
- Compact candidate restaurant list (post-filter)
- Output contract (JSON schema / field list)
- Ranking rubric (fit to cuisine, budget, rating, soft prefs)

### Prompt responsibilities of the model

- Interpret soft preferences against candidate metadata and names
- Rank best-fit restaurants
- Write concise explanations per restaurant
- Stay faithful to provided candidates (no invented restaurants)

### Guardrails

- Only recommend restaurants present in the candidate payload
- Prefer structured JSON over free-form prose for the machine-readable part
- Limit candidate count and explanation length to control latency/cost
- On malformed LLM output: retry once or fall back to rating-sorted candidates with a generic explanation

---

## 8. API Contract (Logical)

### Request

```json
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly, outdoor seating"
}
```

### Response

```json
{
  "summary": "Top Italian picks in Bangalore within a medium budget.",
  "recommendations": [
    {
      "rank": 1,
      "restaurant_name": "...",
      "cuisine": "Italian",
      "rating": 4.4,
      "estimated_cost": "medium",
      "explanation": "..."
    }
  ],
  "meta": {
    "candidates_considered": 25,
    "used_fallback": false
  }
}
```

---

## 9. Non-Functional Considerations

| Area | Approach |
|---|---|
| **Latency** | Preprocess offline; hard-filter before LLM; keep N small |
| **Cost** | Cap tokens via candidate truncation and concise prompts |
| **Reliability** | Validate LLM JSON; fallback ranking path |
| **Observability** | Log filter counts, prompt size, parse failures (no PII beyond preferences) |
| **Security** | Store API keys in env; never commit secrets |
| **Extensibility** | Swap LLM providers via client interface; add embeddings later if needed |

---

## 10. Future Extensions (Out of Scope for v1)

- Semantic search / embeddings over reviews or dishes
- User accounts and preference history
- Map-based UI and distance-aware ranking
- Multi-city caching and incremental dataset refresh
- A/B testing of prompt templates

---

## 11. Architecture Summary

v1 is a **hybrid recommender**:

- **Deterministic filtering** enforces location, cuisine, budget, and rating constraints on the Zomato dataset.
- **LLM reasoning** ranks the shortlisted restaurants and generates human-readable explanations.
- **Presentation** surfaces name, cuisine, rating, cost, and explanation as the primary user outcome.

This keeps recommendations grounded in real restaurant records while using the LLM where it adds the most value: personalization language and preference-aware ranking.
