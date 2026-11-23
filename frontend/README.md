# TasteMatch AI — Next.js frontend

React/Next.js App Router UI for the TasteMatch restaurant recommender. Talks to the FastAPI backend via rewrites.

## Requirements

- Node.js 20+
- FastAPI backend running (default `http://127.0.0.1:8000`)

## Setup

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Dev server on port 3000 |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |

## API proxy

Browser calls `/api/backend/*`, which Next rewrites to `BACKEND_URL` (see `.env.local` / Vercel env).

| Frontend path | Backend |
|---|---|
| `GET /api/backend/meta/locations` | `GET /meta/locations` |
| `POST /api/backend/recommend` | `POST /recommend` |

## Deploy on Vercel

1. Import the GitHub repo in Vercel; set **Root Directory** to `frontend`.
2. Set env var `BACKEND_URL` to your Railway HTTPS URL (no trailing slash).
3. Deploy. Details: [`../Docs/deployment-plan.md`](../Docs/deployment-plan.md).

## Pages

- `/` — preference form + trending curations
- `/results` — ranked picks + AI explanations (from sessionStorage after submit)
