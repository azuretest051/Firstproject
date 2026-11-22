"""Preference schema and validation."""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

VALID_BUDGETS = frozenset({"low", "medium", "high"})
MIN_RATING_MIN = 0.0
MIN_RATING_MAX = 5.0
DEFAULT_MAX_ADDITIONAL_PREFS_LEN = 500


class PreferenceValidationError(ValueError):
    """Raised when user preference input is missing or invalid."""


def _as_mapping(raw: Any) -> Mapping[str, Any]:
    if isinstance(raw, UserPreferences):
        return {
            "location": raw.location,
            "budget": raw.budget,
            "cuisine": raw.cuisine,
            "min_rating": raw.min_rating,
            "additional_preferences": raw.additional_preferences,
        }
    if not isinstance(raw, Mapping):
        raise PreferenceValidationError("Preferences must be a mapping/dict.")
    return raw


def _require_nonempty_string(raw: Mapping[str, Any], key: str) -> str:
    if key not in raw or raw[key] is None:
        raise PreferenceValidationError(f"Missing required field: {key}")
    value = raw[key]
    if not isinstance(value, str):
        value = str(value)
    text = " ".join(value.strip().split())
    if not text:
        raise PreferenceValidationError(
            f"Missing required field: {key} (empty/whitespace is not allowed)"
        )
    return text


def normalize_location(value: str) -> str:
    """Casefold + collapse whitespace for location matching."""
    return " ".join(value.strip().casefold().split())


def normalize_cuisine_tokens(value: str) -> list[str]:
    """Split cuisine input into normalized tokens (any-match policy)."""
    tokens: list[str] = []
    seen: set[str] = set()
    for part in re.split(r"[,|/]", value):
        token = " ".join(part.strip().casefold().split())
        if not token or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    if not tokens:
        raise PreferenceValidationError(
            "Missing required field: cuisine (no usable cuisine tokens)"
        )
    return tokens


def normalize_budget(value: str) -> str:
    budget = value.strip().casefold()
    if budget not in VALID_BUDGETS:
        allowed = ", ".join(sorted(VALID_BUDGETS))
        raise PreferenceValidationError(
            f"Invalid budget '{value}'. Allowed values: {allowed}"
        )
    return budget


def normalize_min_rating(value: Any) -> float:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise PreferenceValidationError("Missing required field: min_rating")
    try:
        rating = float(value)
    except (TypeError, ValueError) as exc:
        raise PreferenceValidationError(
            f"Invalid min_rating '{value}': must be a number between "
            f"{MIN_RATING_MIN} and {MIN_RATING_MAX}"
        ) from exc
    if math.isnan(rating) or math.isinf(rating):
        raise PreferenceValidationError(
            f"Invalid min_rating '{value}': NaN/Inf not allowed"
        )
    if rating < MIN_RATING_MIN or rating > MIN_RATING_MAX:
        raise PreferenceValidationError(
            f"Invalid min_rating '{value}': must be between "
            f"{MIN_RATING_MIN} and {MIN_RATING_MAX}"
        )
    return rating


def normalize_additional_preferences(
    value: Any,
    *,
    max_len: int | None = None,
) -> Optional[str]:
    """Soft preference text — omitted/empty is valid; long text is truncated."""
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    text = " ".join(value.strip().split())
    if not text:
        return None
    limit = max_len
    if limit is None:
        limit = int(os.getenv("MAX_ADDITIONAL_PREFS_LEN", DEFAULT_MAX_ADDITIONAL_PREFS_LEN))
    if len(text) > limit:
        text = text[:limit].rstrip()
    return text


@dataclass(frozen=True)
class UserPreferences:
    """Validated, normalized user preferences for recommendations."""

    location: str
    budget: str
    cuisine: str
    min_rating: float
    additional_preferences: Optional[str] = None
    # Derived normalized fields used by the filtering layer
    location_key: str = field(repr=False, compare=False, default="")
    cuisine_tokens: tuple[str, ...] = field(repr=False, compare=False, default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "budget": self.budget,
            "cuisine": self.cuisine,
            "min_rating": self.min_rating,
            "additional_preferences": self.additional_preferences,
        }


def validate_preferences(raw: Any) -> UserPreferences:
    """Validate and normalize raw preference input.

    Required: location, budget, cuisine, min_rating.
    Optional: additional_preferences (soft text; not hard-filtered).
    """
    data = _as_mapping(raw)

    location_display = _require_nonempty_string(data, "location")
    budget_raw = _require_nonempty_string(data, "budget")
    cuisine_display = _require_nonempty_string(data, "cuisine")

    if "min_rating" not in data:
        raise PreferenceValidationError("Missing required field: min_rating")

    location_key = normalize_location(location_display)
    budget = normalize_budget(budget_raw)
    cuisine_tokens = tuple(normalize_cuisine_tokens(cuisine_display))
    min_rating = normalize_min_rating(data.get("min_rating"))
    additional = normalize_additional_preferences(data.get("additional_preferences"))

    return UserPreferences(
        location=location_display,
        budget=budget,
        cuisine=cuisine_display,
        min_rating=min_rating,
        additional_preferences=additional,
        location_key=location_key,
        cuisine_tokens=cuisine_tokens,
    )
