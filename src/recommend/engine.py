"""Orchestrate validate → filter → Groq LLM rank → mapped response."""

from __future__ import annotations

import logging
from typing import Any, Optional

import pandas as pd

from src.data.store import StoreError
from src.filtering.filter import FilterResult, get_candidates
from src.llm.client import LLMClient
from src.llm.ranker import rank_candidates
from src.preferences.schema import PreferenceValidationError, UserPreferences

logger = logging.getLogger(__name__)


def _normalize_recommendation_item(item: dict[str, Any], rank: int) -> dict[str, Any]:
    return {
        "rank": rank,
        "restaurant_name": item.get("restaurant_name") or item.get("name") or "",
        "cuisine": item.get("cuisine"),
        "rating": item.get("rating"),
        "estimated_cost": item.get("estimated_cost"),
        "explanation": item.get("explanation")
        or "Matches your selected location, cuisine, budget, and rating filters.",
        "location": item.get("location"),
        "cost_for_two": item.get("cost_for_two"),
    }


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    recommendations = [
        _normalize_recommendation_item(item, i)
        for i, item in enumerate(payload.get("recommendations") or [], start=1)
        if isinstance(item, dict)
    ]
    meta = dict(payload.get("meta") or {})
    used_fallback = bool(meta.get("used_fallback", False))
    no_matches = bool(meta.get("no_matches", False)) or len(recommendations) == 0 and meta.get(
        "match_count", 0
    ) == 0

    if no_matches:
        status = "no_matches"
    elif used_fallback:
        status = "llm_fallback"
    else:
        status = "ok"

    meta.update(
        {
            "used_fallback": used_fallback,
            "no_matches": no_matches,
            "status": status,
            "candidates_considered": int(meta.get("candidates_considered") or 0),
            "match_count": int(meta.get("match_count") or 0),
            "capped": bool(meta.get("capped", False)),
        }
    )
    return {
        "summary": payload.get("summary") or "",
        "recommendations": recommendations,
        "meta": meta,
    }


def recommend(
    preferences: dict | UserPreferences,
    *,
    restaurants: Optional[pd.DataFrame] = None,
    top_n: int | None = None,
    client: Optional[LLMClient] = None,
    store_path=None,
) -> dict[str, Any]:
    """Run hard filtering then Groq ranking/explanations.

    Returns a stable architecture-shaped payload with ``summary``,
    ``recommendations``, and ``meta`` (including ``status``).
    """
    try:
        filtered: FilterResult = get_candidates(
            preferences,
            restaurants=restaurants,
            top_n=top_n,
            store_path=store_path,
        )
    except PreferenceValidationError:
        raise
    except StoreError:
        raise

    if filtered.empty:
        return _normalize_payload(
            {
                "summary": (
                    "No restaurants matched your filters. "
                    "Try relaxing location, cuisine, budget, or minimum rating."
                ),
                "recommendations": [],
                "meta": {
                    "candidates_considered": 0,
                    "match_count": 0,
                    "used_fallback": False,
                    "no_matches": True,
                    "capped": False,
                },
            }
        )

    try:
        ranked = rank_candidates(
            filtered.preferences,
            filtered.candidates,
            client=client,
        )
    except Exception as exc:  # noqa: BLE001 - map unexpected failures to fallback payload
        logger.exception("Unexpected ranking failure")
        from src.llm.parser import fallback_recommendations

        ranked = fallback_recommendations(
            filtered.candidates,
            reason=f"unexpected_error: {exc}",
        )

    meta = dict(ranked.get("meta") or {})
    meta.update(
        {
            "match_count": filtered.match_count,
            "candidates_considered": int(len(filtered.candidates)),
            "capped": filtered.capped,
            "no_matches": False,
        }
    )
    ranked["meta"] = meta
    return _normalize_payload(ranked)
