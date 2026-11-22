"""Parse, ground, and fall back for Groq recommendation responses."""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd


class ParseError(ValueError):
    """Raised when LLM output cannot be parsed into grounded recommendations."""


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_object(raw: str) -> dict[str, Any]:
    """Extract a JSON object from raw LLM text (including markdown fences)."""
    if raw is None:
        raise ParseError("Empty LLM response.")
    text = str(raw).strip()
    if not text:
        raise ParseError("Empty LLM response.")

    fence = _FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise ParseError("LLM response is not valid JSON.")
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ParseError(f"LLM response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ParseError("LLM JSON root must be an object.")
    return data


def _candidate_index(candidates: pd.DataFrame | list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if isinstance(candidates, pd.DataFrame):
        rows = candidates.to_dict(orient="records")
    else:
        rows = list(candidates)

    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = str(row.get("name", "")).strip()
        if not name:
            continue
        key = name.casefold()
        # First occurrence wins (candidates already rating-sorted)
        if key not in index:
            index[key] = row
    return index


def _store_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "restaurant_name": row.get("name"),
        "cuisine": row.get("cuisines_raw") or row.get("cuisine_tokens_str"),
        "rating": row.get("rating"),
        "estimated_cost": row.get("budget_band"),
        "location": row.get("location_raw") or row.get("location"),
        "cost_for_two": row.get("cost"),
    }


def fallback_recommendations(
    candidates: pd.DataFrame | list[dict[str, Any]],
    *,
    limit: int | None = None,
    reason: str = "AI ranking unavailable",
) -> dict[str, Any]:
    """Rating-sorted fallback with generic explanations."""
    if isinstance(candidates, pd.DataFrame):
        rows = candidates.to_dict(orient="records")
    else:
        rows = list(candidates)

    if limit is not None:
        rows = rows[:limit]

    recommendations = []
    for i, row in enumerate(rows, start=1):
        fields = _store_fields(row)
        recommendations.append(
            {
                "rank": i,
                **fields,
                "explanation": (
                    "Top-rated match for your filters "
                    "(AI ranking unavailable)."
                ),
            }
        )

    return {
        "summary": (
            "Showing top-rated restaurants from your filters "
            "(AI ranking was unavailable)."
        ),
        "recommendations": recommendations,
        "meta": {
            "used_fallback": True,
            "fallback_reason": reason,
        },
    }


def parse_recommendations(
    raw: str,
    candidates: pd.DataFrame | list[dict[str, Any]],
) -> dict[str, Any]:
    """Parse LLM JSON, ground to candidates, and normalize ranks.

    Structured factual fields are taken from the store candidate (L09).
    Unknown / invented restaurant names are dropped (L05).
    """
    data = extract_json_object(raw)
    items = data.get("recommendations")
    if not isinstance(items, list):
        raise ParseError("LLM JSON missing 'recommendations' array.")

    index = _candidate_index(candidates)
    grounded: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("restaurant_name") or item.get("name")
        if not name:
            continue
        key = str(name).strip().casefold()
        if key not in index or key in seen:
            continue
        seen.add(key)
        row = index[key]
        fields = _store_fields(row)
        explanation = item.get("explanation")
        if explanation is None or not str(explanation).strip():
            explanation = "Matches your selected location, cuisine, budget, and rating filters."
        grounded.append(
            {
                "rank": len(grounded) + 1,
                **fields,
                "explanation": str(explanation).strip(),
            }
        )

    if not grounded:
        raise ParseError(
            "No grounded recommendations remained after validating LLM output "
            "against the candidate list."
        )

    summary = data.get("summary")
    if not summary or not str(summary).strip():
        summary = "Ranked restaurant picks based on your preferences."

    return {
        "summary": str(summary).strip(),
        "recommendations": grounded,
        "meta": {
            "used_fallback": False,
            "parsed_count": len(grounded),
            "llm_raw_count": len(items),
        },
    }
