# Edge Cases & Corner Scenarios

## AI-Powered Restaurant Recommendation System (Zomato Use Case)

Catalog of edge cases and corner scenarios derived from [`architecture.md`](./architecture.md) and [`implementation-plan.md`](./implementation-plan.md). Use this during Phases 1–6 for validation, tests, and fallback design.

**Legend**

| Severity | Meaning |
|---|---|
| **P0** | Breaks core flow or produces wrong/unsafe output; must handle in v1 |
| **P1** | Degrades quality or UX; should handle in v1 |
| **P2** | Rare / polish; handle if time allows |

---

## 1. Data Ingestion & Store (Phase 1)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| D01 | Hugging Face dataset download fails (network / 401 / timeout) | Clear error; do not overwrite a good processed store with partial data | P0 |
| D02 | Dataset schema differs from expected column names | Fail fast with a schema-mismatch message; do not silently drop all rows | P0 |
| D03 | Missing / null restaurant name | Drop or flag row; never surface blank names in recommendations | P0 |
| D04 | Missing location / city | Exclude from location-filtered queries or place in `unknown` bucket that never matches normal city filters | P0 |
| D05 | Missing or non-numeric rating (`NEW`, `-`, empty) | Treat as unscored; exclude when `min_rating` is set, or allow only if user sets no min | P0 |
| D06 | Missing / invalid cost | Leave budget band unset; exclude from budget-filtered queries | P0 |
| D07 | Cuisine is empty, `"NA"`, or multi-value string (`"Italian, Chinese"`) | Tokenize multi-cuisine; empty cuisine never matches a specific cuisine filter | P0 |
| D08 | Duplicate restaurant rows (same name + location) | Dedupe or keep highest-rated / most complete row | P1 |
| D09 | Extreme cost outliers skewing budget percentiles | Use robust banding (quantiles / fixed thresholds), not mean±std alone | P1 |
| D10 | Very large dataset load OOMs or is slow | Stream/chunk ingest; persist processed file; load processed store at runtime, not raw HF every request | P1 |
| D11 | Processed store file missing or corrupt at startup | Fail with “run ingest first” guidance; do not call LLM on empty memory | P0 |
| D12 | Re-ingest while app is reading store | Atomic write (temp file → replace) to avoid half-written reads | P1 |
| D13 | Unicode / special characters in names (`Café`, `&`, quotes) | Preserve safely through store, prompt JSON, and UI escaping | P1 |
| D14 | Inconsistent location spellings (`Bangalore` vs `bengaluru` vs `Bangalor`) | Normalize case/whitespace; document known aliases if supported; otherwise no fuzzy match in v1 | P1 |

---

## 2. User Preferences & Validation (Phase 2)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| P01 | Missing required fields (location / budget / cuisine) | 400-style validation error before filtering | P0 |
| P02 | Empty strings or whitespace-only inputs | Treat as missing; reject or normalize | P0 |
| P03 | Invalid budget value (not `low`/`medium`/`high`) | Reject with allowed values listed | P0 |
| P04 | `min_rating` out of range (e.g. `-1`, `6`, `NaN`) | Reject; document valid range (e.g. 0–5) | P0 |
| P05 | `min_rating` at exact boundary (e.g. `4.0` when rating is `4.0`) | Inclusive match (`rating >= min_rating`) | P0 |
| P06 | Cuisine case / spacing variants (`italian`, `Italian `, `ITAlian`) | Casefold + trim before matching | P0 |
| P07 | Multiple cuisines requested (`Italian, Chinese`) | Match restaurants that satisfy any or all (document policy); prefer **any-match** for v1 unless specified | P1 |
| P08 | Cuisine not present anywhere in dataset | Empty candidates; friendly “no matches” (do not invent results) | P0 |
| P09 | Location not in dataset | Empty candidates; suggest checking spelling / available cities if feasible | P0 |
| P10 | `additional_preferences` empty / omitted | Valid; LLM ranks on hard prefs only | P0 |
| P11 | Extremely long `additional_preferences` (thousands of chars) | Truncate with limit; avoid blowing prompt token budget | P1 |
| P12 | Conflicting prefs (e.g. `budget=low` + soft pref “fine dining tasting menu”) | Hard filters win; LLM may note tradeoff in explanation/summary | P1 |
| P13 | Soft prefs that cannot be verified from data (“halal”, “wheelchair ramp”) when fields absent | LLM must not claim verified amenities; hedge or ignore unverifiable claims | P0 |
| P14 | Injection-like text in free-text prefs (“ignore instructions…”) | Treat as user preference text only; system prompt + JSON schema take precedence | P0 |
| P15 | Non-English location/cuisine input | Best-effort normalize; if no match → empty results, not crash | P1 |

---

## 3. Hard Filtering & Candidate Selection (Phase 2)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| F01 | Zero restaurants after filters | Skip LLM; return empty list + clear message | P0 |
| F02 | Exactly one restaurant matches | Still return one recommendation (LLM optional; ranking trivial) | P0 |
| F03 | Huge match set (thousands of rows) | Cap to top-N by rating (or rating×votes); set `candidates_considered` accurately | P0 |
| F04 | All matches share identical rating | Stable secondary sort (name / cost) so order is deterministic before LLM | P1 |
| F05 | Cuisine substring false positives (`Thai` matching `Thailand` token noise, or `Chi` → `Chinese`) | Prefer token-boundary / list membership over raw substring where possible | P1 |
| F06 | Multi-cuisine restaurant partially matches | Include if any requested cuisine token matches | P0 |
| F07 | Budget band boundary restaurants | Assign each row to one band at ingest; filtering uses that band only | P0 |
| F08 | User filters so strict that only low-quality rows remain after N-cap | Still return them; summary may note limited options | P1 |
| F09 | Filter combination valid but processed store empty | Same as F01 / D11 — explicit empty-store error vs empty-filter result | P0 |

---

## 4. Prompt Construction & LLM Reasoning (Phase 3)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| L01 | LLM API key missing / invalid | Fail with config error; optional fallback ranking **without** AI explanations, flagged `used_fallback=true` | P0 |
| L02 | LLM timeout / 429 rate limit / 5xx | Retry once with backoff; then fallback ranking | P0 |
| L03 | LLM returns non-JSON / markdown-wrapped JSON | Strip fences if present; parse; else retry/fallback | P0 |
| L04 | LLM returns JSON missing required fields | Reject parse; retry/fallback | P0 |
| L05 | LLM invents restaurants not in candidate list | Drop unknown names; keep only grounded items; if none left → fallback | P0 |
| L06 | LLM returns duplicate restaurants | Dedupe by name (+ location); re-rank densely | P1 |
| L07 | LLM returns fewer items than candidates | Accept; UI shows returned set | P1 |
| L08 | LLM returns more items than candidates / padded noise | Truncate to known candidates only | P0 |
| L09 | LLM alters facts (wrong rating/cost/cuisine) | Prefer store values for structured fields; use LLM for rank + explanation text | P0 |
| L10 | Explanations empty or generic for all items | Accept structurally; optionally regenerate once; else show with weaker copy | P1 |
| L11 | Soft preference contradicts all candidates | Rank best available; summary states no perfect match | P1 |
| L12 | Prompt exceeds model context (too many candidates / long prefs) | Enforce N + truncation before call; never send unbounded lists | P0 |
| L13 | Model refuses / safety block on benign food query | Fallback ranking; log refusal category | P1 |
| L14 | Streaming vs non-streaming partial output | v1: use full completion only; do not parse partial JSON | P1 |
| L15 | Non-deterministic rankings across identical requests | Accept for v1; optional temperature=0 for demos/tests | P2 |

---

## 5. Orchestration & API (Phase 4)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| A01 | Malformed JSON body / wrong types | 422/400 with field-level errors | P0 |
| A02 | Extra unknown fields in request | Ignore or reject per schema policy (document one) | P2 |
| A03 | Concurrent recommend requests while store loading | Thread-safe read of processed data; no race crashes | P1 |
| A04 | LLM success but mapper fails | Return controlled 500/error payload; never leak stack traces to UI | P0 |
| A05 | Empty filter result vs LLM failure | Distinguish in response: `no_matches` vs `llm_fallback` / error | P0 |
| A06 | Fallback path engaged | `meta.used_fallback=true`; explanations marked generic | P0 |
| A07 | Very slow end-to-end call | Timeout budget on LLM; return fallback or timeout error before UI hangs forever | P1 |
| A08 | Idempotent repeated identical requests | Safe to repeat; no duplicate side effects (v1 is read-only) | P2 |

---

## 6. UI / Output Display (Phase 5)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| U01 | User submits empty form | Inline validation; no API call | P0 |
| U02 | No matches | Friendly empty state; tips to relax filters (budget / rating / cuisine) | P0 |
| U03 | Fallback recommendations shown | Banner/note: “AI ranking unavailable — showing top-rated matches” | P0 |
| U04 | Long restaurant names / explanations overflow layout | Truncate with expand/wrap; no horizontal breakage | P1 |
| U05 | Special characters / HTML-like strings in names or LLM text | Escape/sanitize for XSS if web UI | P0 |
| U06 | Double-click submit / rapid resubmit | Disable button / debounce while request in flight | P1 |
| U07 | API down mid-session | Error toast with retry; preserve entered form values | P1 |
| U08 | Zero-decimal vs one-decimal ratings display | Consistent formatting (e.g. one decimal) | P2 |
| U09 | Mobile narrow viewport | Inputs and result cards remain usable | P1 |
| U10 | Summary present but recommendations empty (inconsistent payload) | Prefer recommendations; hide empty summary or show error | P1 |

---

## 7. Budget, Rating & Ranking Corner Logic

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| B01 | Cost exactly on band cutover threshold | Deterministic assignment at ingest; document cutoffs | P0 |
| B02 | `budget=high` but city only has cheap options | Empty or sparse results; message that few/no high-budget matches exist | P1 |
| B03 | User wants high rating + low budget + rare cuisine | Likely F01; guide user to loosen one constraint | P1 |
| B04 | Ratings stored as strings (`"4.5"`) after ingest bug | Coerce at ingest; filters must see numeric types | P0 |
| B05 | Ties in LLM ranks (`rank: 1` twice) | Normalize to unique dense ranks in parser | P1 |
| B06 | Rank order disagrees with rating order due to soft prefs | Allowed; explanations should reflect the soft-pref reason | P1 |

---

## 8. Security, Privacy & Config

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| S01 | API key committed or printed in logs | Never log secrets; `.env` gitignored; `.env.example` only | P0 |
| S02 | User pastes personal data into preferences | Minimize logging of raw free text in production-like setups | P1 |
| S03 | Prompt injection via restaurant names in dataset | System instructions forbid following candidate-embedded instructions | P1 |
| S04 | Untrusted LLM content rendered as HTML | Text-only render / sanitize | P0 |

---

## 9. Cross-Cutting Operational Cases (Phase 6)

| ID | Scenario | Expected behavior | Sev |
|---|---|---|---|
| O01 | First run before ingest | Clear setup error, not a generic crash | P0 |
| O02 | Stale processed data after dataset update | Document re-ingest; optional version/hash in meta | P2 |
| O03 | Dependency version conflicts on fresh install | Pin versions in requirements; README notes Python version | P1 |
| O04 | Offline mode (no LLM network) | Fallback ranking path still usable for demo of filters | P1 |
| O05 | Partial test environment without API key | Unit tests mock LLM; integration tests skip if no key | P1 |

---

## 10. Priority Test Matrix (v1 Must-Pass)

These scenarios should have automated or manual checks before calling v1 done:

1. **F01 / U02** — No matches → empty state, no hallucinated restaurants  
2. **P05 / F06** — Boundary rating + multi-cuisine token match  
3. **F03 / L12** — Large match set capped; prompt stays bounded  
4. **L03 / L05 / A06** — Bad JSON + invented names → parse reject / grounded filter / fallback flag  
5. **L01 / O04** — Missing key or offline → controlled fallback or clear config error  
6. **P14 / S04** — Injection-like prefs + unsafe LLM strings handled safely in UI  
7. **D05 / D07** — Dirty ratings/cuisines cleaned so filters behave predictably  
8. **U01 / A01** — Invalid input rejected before LLM spend  

---

## 11. Handling Patterns (Summary)

| Pattern | Use when |
|---|---|
| **Reject (validation)** | Bad/missing user input, invalid enums/ranges |
| **Empty result** | Valid query, zero hard-filter matches |
| **Cap + truncate** | Too many candidates or oversized free text |
| **Retry once** | Transient LLM/network failures, minor parse issues |
| **Fallback rank** | LLM unavailable or unparseable; set `used_fallback` |
| **Grounding filter** | Drop any LLM item not in candidate set |
| **Store wins on facts** | Name/cuisine/rating/cost come from dataset, not LLM prose |
| **Fail fast on ingest/store** | Missing schema, corrupt/missing processed data |

---

## 12. Mapping to Implementation Phases

| Phase | Edge-case groups to implement/test |
|---|---|
| 1 | D01–D14 |
| 2 | P01–P15, F01–F09, B01–B04 |
| 3 | L01–L15, B05–B06 |
| 4 | A01–A08 |
| 5 | U01–U10 |
| 6 | S01–S04, O01–O05, Priority Test Matrix |

This document should be updated if new filters, LLM providers, or UI behaviors are introduced beyond v1.
