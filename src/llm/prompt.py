"""Prompt templates for ranking and explaining restaurants via Groq."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from src.preferences.schema import UserPreferences

SYSTEM_PROMPT = """You are a restaurant recommendation assistant.
You must rank ONLY from the provided candidate restaurants.
Never invent restaurants, ratings, costs, or cuisines.
Use the candidate data as the source of truth for factual fields.
Soft preferences may influence ranking and explanations, but do not claim
amenities that are not supported by the candidate fields.
Return valid JSON only — no markdown fences, no prose outside JSON."""


def _candidate_payload(candidates: pd.DataFrame | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(candidates, pd.DataFrame):
        rows = candidates.to_dict(orient="records")
    else:
        rows = list(candidates)

    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append(
            {
                "restaurant_name": row.get("name"),
                "location": row.get("location_raw") or row.get("location"),
                "cuisine": row.get("cuisines_raw") or row.get("cuisine_tokens_str"),
                "rating": row.get("rating"),
                "estimated_cost": row.get("budget_band"),
                "cost_for_two": row.get("cost"),
                "votes": row.get("votes"),
                "rest_type": row.get("rest_type"),
                "online_order": row.get("online_order"),
                "book_table": row.get("book_table"),
            }
        )
    return payload


def build_recommendation_prompt(
    preferences: UserPreferences,
    candidates: pd.DataFrame | list[dict[str, Any]],
) -> str:
    """Build the user prompt for Groq ranking + explanations."""
    candidate_list = _candidate_payload(candidates)
    prefs = {
        "location": preferences.location,
        "budget": preferences.budget,
        "cuisine": preferences.cuisine,
        "min_rating": preferences.min_rating,
        "additional_preferences": preferences.additional_preferences,
    }

    output_contract = {
        "summary": "Short overview of the picks",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": "Exact name from candidates",
                "cuisine": "From candidate data",
                "rating": 4.5,
                "estimated_cost": "low|medium|high",
                "explanation": "Why this fits the user preferences",
            }
        ],
    }

    return f"""Rank the candidate restaurants for this user and explain each pick.

User preferences (JSON):
{json.dumps(prefs, ensure_ascii=False, indent=2)}

Candidate restaurants (JSON array — recommend ONLY from these):
{json.dumps(candidate_list, ensure_ascii=False, indent=2)}

Instructions:
1. Rank the best-fitting candidates (you may return fewer than all candidates).
2. Prefer stronger cuisine/budget/rating fit; use additional_preferences only as soft signal.
3. restaurant_name MUST exactly match a candidate restaurant_name.
4. For cuisine, rating, and estimated_cost, copy values from the matched candidate.
5. Keep explanations concise (1-2 sentences).
6. Respond with JSON matching this shape:
{json.dumps(output_contract, ensure_ascii=False, indent=2)}
"""


def build_messages(
    preferences: UserPreferences,
    candidates: pd.DataFrame | list[dict[str, Any]],
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt)."""
    return SYSTEM_PROMPT, build_recommendation_prompt(preferences, candidates)
