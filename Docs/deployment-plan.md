# Deployment Plan

## TasteMatch AI — Free Hosting (Vercel + Railway)

Deploy the **Next.js frontend** on [Vercel](https://vercel.com) and the **FastAPI backend** on [Railway](https://railway.app), both on free/hobby tiers. The LLM stays on **Groq** (free API key).

---

## 1. Target architecture

```text
Browser
   │
   ▼
Vercel (Next.js)  ──rewrite──▶  Railway (FastAPI + SQLite)
   │                                │
   │                                ▼
   │                             Groq API (LLM)
   └─ /api/backend/*  →  https://<railway-app>.up.railway.app/*
```

| Layer | Host | What ships |
|---|---|---|
| Frontend | Vercel | `frontend/` (App Router) |
| Backend | Railway | Python app: `src/`, `requirements.txt`, processed SQLite |
| LLM | Groq | `GROQ_API_KEY` only (no model hosting) |

**Why this split works for this repo**

- The frontend already calls `/api/backend/...` and Next rewrites that path using `BACKEND_URL` (`frontend/next.config.ts`).
- Browser traffic stays same-origin on Vercel, so **CORS is not required** for the normal UI flow.
- FastAPI + SQLite fits a single Railway web service for a demo/v1.

---

## 2. Prerequisites

### Accounts

1. [GitHub](https://github.com) — repo hosting (both platforms deploy from Git)
2. [Railway](https://railway.app) — free/trial credits; link GitHub
3. [Vercel](https://vercel.com) — Hobby plan; link GitHub
4. [Groq](https://console.groq.com) — API key

### Local readiness checklist

- [ ] Project builds locally: API on `:8000`, Next on `:3000`
- [ ] `data/processed/restaurants.sqlite` exists (run `python -m src.data.ingest` if missing)
- [ ] `.env` works locally with a valid `GROQ_API_KEY`
- [ ] Code pushed to a GitHub repository (public or private)
- [ ] Secrets never committed (`.env`, `.env.local` stay gitignored)

### Important data note

`.gitignore` excludes:

- `data/processed/*`
- `*.sqlite`

Railway will **not** get the restaurant DB from a normal `git push`. You must ship the SQLite file separately (see §4.3). Without it, `/meta/locations` and `/recommend` return store errors.

---

## 3. Deployment order

Do backend first, then frontend.

```text
1. Push code to GitHub
2. Deploy FastAPI on Railway → get public HTTPS URL
3. Upload / provision restaurants.sqlite on Railway
4. Set Groq + path env vars on Railway
5. Deploy Next.js on Vercel with BACKEND_URL = Railway URL
6. Smoke-test health → locations → recommend → full UI
```

---

## 4. Backend — Railway

### 4.1 Create the service

1. Open Railway → **New Project** → **Deploy from GitHub repo**.
2. Select this repository.
3. Add a **Web Service** rooted at the **repo root** (not `frontend/`).
4. Railway should detect Python via `requirements.txt`.

### 4.2 Start command & runtime

Use a start command that binds to Railway’s `PORT`:

```bash
uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
```

Suggested service settings:

| Setting | Value |
|---|---|
| Root directory | `/` (repository root) |
| Build | Nixpacks Python provider (auto `pip install -r requirements.txt`) |
| Start | command above |
| Watch paths | optional; redeploy on push to `main` |

Do **not** set a custom Railway build command to bare `pip install ...` — on Nixpacks that often fails with `pip: command not found`. Leave build empty and use `nixpacks.toml` + `requirements.txt`.

Optional `Procfile` at repo root (Railway respects it):

```text
web: uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
```

Optional `runtime.txt` if you want a pinned Python (example):

```text
python-3.12.8
```

### 4.3 Ship the SQLite database

Pick **one** approach:

#### Option A — Force-commit the processed DB (simplest for demos)

1. Locally ensure ingest has run: `python -m src.data.ingest`
2. Temporarily allow the file in git, e.g. add an exception in `.gitignore`:

   ```gitignore
   !data/processed/restaurants.sqlite
   ```

3. Commit and push `data/processed/restaurants.sqlite` (~9 MB today).
4. Keep `PROCESSED_DATA_PATH=data/processed/restaurants.sqlite` on Railway.

#### Option B — Railway volume + one-time upload (cleaner long-term)

1. Attach a **Volume** mounted at e.g. `/data`.
2. Upload `restaurants.sqlite` into that volume (Railway CLI / dashboard file upload, or a one-off shell).
3. Set:

   ```text
   PROCESSED_DATA_PATH=/data/restaurants.sqlite
   ```

#### Option C — Ingest on first deploy (slow, needs HF network)

1. Add a release/start hook that runs `python -m src.data.ingest` if the DB is missing.
2. Expect longer first boot and Hugging Face download limits.
3. Prefer A or B for a reliable demo.

**Recommendation for this project:** Option A for the first public demo; move to Option B if the DB grows or you want secrets/data out of git.

### 4.4 Backend environment variables (Railway)

Set these in the Railway service **Variables** tab:

| Variable | Required | Example / notes |
|---|---|---|
| `GROQ_API_KEY` | Yes (for real LLM ranks) | From Groq console |
| `LLM_BASE_URL` | No | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | No | `openai/gpt-oss-20b` (or your preferred Groq model) |
| `LLM_TEMPERATURE` | No | `0.2` |
| `LLM_MAX_TOKENS` | No | `1024` |
| `LLM_TIMEOUT_SECONDS` | No | `30` |
| `LLM_MAX_RETRIES` | No | `1` |
| `CANDIDATE_TOP_N` | No | `25` |
| `MAX_ADDITIONAL_PREFS_LEN` | No | `500` |
| `PROCESSED_DATA_PATH` | Yes if not default | `data/processed/restaurants.sqlite` or volume path |
| `PORT` | Auto | Provided by Railway — do not hardcode |

Without `GROQ_API_KEY`, the engine still runs via **rating-sorted fallback** (`meta.used_fallback=true`), which is fine for smoke tests.

### 4.5 Public URL

1. Railway → service → **Settings** → **Networking** → **Generate domain**.
2. Copy the HTTPS URL, e.g. `https://tastematch-api-production.up.railway.app`.
3. Verify:

```bash
curl https://<your-railway-domain>/health
# expect: {"status":"ok"}

curl https://<your-railway-domain>/meta/locations
# expect: JSON with cities / locations
```

### 4.6 Optional: CORS (only if calling Railway from the browser directly)

Normal Vercel rewrites do **not** need CORS. Add CORS later only if a browser hits the Railway URL from another origin. Not required for this plan’s default path.

---

## 5. Frontend — Vercel

### 5.1 Create the project

1. Open Vercel → **Add New Project** → import the same GitHub repo.
2. Configure:

| Setting | Value |
|---|---|
| Framework Preset | Next.js |
| Root Directory | `frontend` |
| Build Command | `npm run build` (default) |
| Output | Next default |
| Install Command | `npm install` (default) |
| Node.js | 20.x or newer |

### 5.2 Frontend environment variables (Vercel)

| Variable | Environment | Value |
|---|---|---|
| `BACKEND_URL` | Production (and Preview if desired) | `https://<your-railway-domain>` — **no trailing slash** |

Notes:

- `BACKEND_URL` is read in `frontend/next.config.ts` for rewrites (`/api/backend/:path*` → `${BACKEND_URL}/:path*`).
- Set it **before** the first production build (or redeploy after adding it).
- Do **not** put `GROQ_API_KEY` on Vercel — the LLM key belongs only on Railway.

Optional local mirror:

```text
# frontend/.env.local
BACKEND_URL=https://<your-railway-domain>
```

### 5.3 Deploy

1. Click **Deploy**.
2. Vercel assigns a URL like `https://tastematch-ai.vercel.app`.
3. Open the site and confirm the home page loads.

### 5.4 How the proxy works in production

| Browser request | Vercel rewrite destination |
|---|---|
| `GET /api/backend/meta/locations` | `GET {BACKEND_URL}/meta/locations` |
| `POST /api/backend/recommend` | `POST {BACKEND_URL}/recommend` |

Client code in `frontend/src/lib/api.ts` keeps using `/api/backend` — no production code change required if rewrites + `BACKEND_URL` are set.

---

## 6. End-to-end verification

Run after both deploys succeed:

1. **Backend health**  
   `GET https://<railway>/health` → `{"status":"ok"}`

2. **Locations**  
   `GET https://<railway>/meta/locations` → non-empty `cities` / `locations`

3. **Recommend (API)**  

   ```bash
   curl -X POST https://<railway>/recommend ^
     -H "Content-Type: application/json" ^
     -d "{\"location\":\"Bangalore\",\"budget\":\"medium\",\"cuisine\":\"Italian\",\"min_rating\":4.0,\"additional_preferences\":\"family-friendly\"}"
   ```

   Expect `summary`, `recommendations[]`, and `meta`.

4. **Frontend UI**  
   - Open Vercel URL  
   - Location dropdown populates  
   - Submit preferences  
   - `/results` shows ranked cards + explanations  

5. **Failure paths**  
   - Empty filters → empty/no-match messaging  
   - Missing Groq key → fallback ranking still returns results  

---

## 7. Free-tier limits & operational notes

| Topic | What to expect |
|---|---|
| Railway credits | Free/trial allotment is limited; monitor usage in the dashboard |
| Cold starts | Free/idle services may sleep; first request after idle can take tens of seconds |
| SQLite | Fine for demo traffic; not for multi-instance write-heavy scale |
| Groq rate limits | Free tier quotas apply; fallback ranking covers soft failures |
| Vercel Hobby | Adequate for this Next app; serverless rewrite latency is usually small vs LLM time |
| Secrets | Rotate Groq key if exposed; never commit `.env` |

---

## 8. Repo deploy assets (implemented)

These files are in the repository to match this plan:

| Item | Status | Purpose |
|---|---|---|
| Root `Procfile` | Done | Railway start: `uvicorn ... --port $PORT` |
| `runtime.txt` | Done | Pin Python 3.12.8 |
| `.gitignore` exception for `restaurants.sqlite` | Done | Option A — commit processed DB for demos |
| `railway.toml` + `nixpacks.toml` | Done | Build/start + `/health` check |
| `frontend/vercel.json` | Done | Next.js build/install defaults |
| `/health` store readiness | Done | Returns `store_ready` (+ `degraded` if SQLite missing) |
| `CORS_ORIGINS` on API | Done | Optional; default `*` for demos |
| CI smoke test | Optional later | `curl` health + locations on each deploy |

**Commit reminder:** after pulling these changes, ensure `data/processed/restaurants.sqlite` is tracked (`git add data/processed/restaurants.sqlite`) before pushing to GitHub for Railway.

---

## 9. Rollback & redeploy

- **Frontend:** Vercel → Deployments → promote a previous successful deployment.
- **Backend:** Railway → Deployments → redeploy prior image/commit.
- **Config mistakes:** Fix env vars first, then redeploy (especially `BACKEND_URL` / `PROCESSED_DATA_PATH` / `GROQ_API_KEY`).

---

## 10. Definition of done (deployed demo)

The free deploy is complete when:

1. Railway serves `/health` and `/meta/locations` over HTTPS.
2. `/recommend` returns ranked restaurants (LLM or fallback).
3. Vercel hosts the TasteMatch UI and `BACKEND_URL` rewrites succeed.
4. A non-technical user can open the Vercel URL, set preferences, and see explained results.
5. No secrets are in the Git history.

---

## 11. Quick reference

```text
GitHub repo
 ├─ Railway  ← root, uvicorn, SQLite, GROQ_API_KEY
 └─ Vercel   ← frontend/, BACKEND_URL=https://<railway-domain>
```

| Service | URL pattern |
|---|---|
| API docs (optional) | `https://<railway>/docs` |
| UI | `https://<project>.vercel.app` |
| Local pair | API `127.0.0.1:8000` + Next `localhost:3000` |

---

## Related docs

- [`architecture.md`](./architecture.md) — system design
- [`implementation-plan.md`](./implementation-plan.md) — build phases
- [`../frontend/README.md`](../frontend/README.md) — frontend scripts & proxy
- [`../README.md`](../README.md) — local run instructions
