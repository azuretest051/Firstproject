"""Rank filtered candidates with Groq, with parse retry and fallback."""

from __future__ import annotations

import logging
from typing import Any, Optional

import pandas as pd

from src.llm.client import LLMClient, LLMError
from src.llm.config import LLMConfigError
from src.llm.parser import ParseError, fallback_recommendations, parse_recommendations
from src.llm.prompt import SYSTEM_PROMPT, build_recommendation_prompt
from src.preferences.schema import UserPreferences

logger = logging.getLogger(__name__)


def rank_candidates(
    preferences: UserPreferences,
    candidates: pd.DataFrame | list[dict[str, Any]],
    *,
    client: Optional[LLMClient] = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Ask Groq to rank/explain candidates; fall back on failure.

    Returns a payload with ``summary``, ``recommendations``, and ``meta``.
    """
    if isinstance(candidates, pd.DataFrame):
        frame = candidates
    else:
        frame = pd.DataFrame(candidates)

    if frame.empty:
        return {
            "summary": "No restaurants matched your filters.",
            "recommendations": [],
            "meta": {
                "used_fallback": False,
                "no_matches": True,
                "candidates_considered": 0,
            },
        }

    working = frame if limit is None else frame.head(limit)
    prompt = build_recommendation_prompt(preferences, working)

    try:
        llm = client or LLMClient()
    except LLMConfigError as exc:
        logger.warning("LLM config unavailable; using fallback ranking: %s", exc)
        result = fallback_recommendations(working, reason=str(exc))
        result["meta"]["candidates_considered"] = int(len(working))
        return result

    raw: str | None = None
    last_parse_error: Exception | None = None

    # Attempt completion + parse; on parse failure, retry completion once.
    for attempt in range(2):
        try:
            raw = llm.complete(prompt, system=SYSTEM_PROMPT)
            parsed = parse_recommendations(raw, working)
            parsed["meta"]["candidates_considered"] = int(len(working))
            parsed["meta"]["provider"] = "groq"
            parsed["meta"]["model"] = llm.config.model
            return parsed
        except LLMError as exc:
            logger.warning("Groq completion failed: %s", exc)
            result = fallback_recommendations(working, reason=str(exc))
            result["meta"]["candidates_considered"] = int(len(working))
            return result
        except ParseError as exc:
            last_parse_error = exc
            logger.warning(
                "Failed to parse Groq response (attempt %s): %s",
                attempt + 1,
                exc,
            )
            continue

    result = fallback_recommendations(
        working,
        reason=f"parse_failed: {last_parse_error}",
    )
    result["meta"]["candidates_considered"] = int(len(working))
    if raw is not None:
        result["meta"]["raw_preview"] = str(raw)[:200]
    return result
