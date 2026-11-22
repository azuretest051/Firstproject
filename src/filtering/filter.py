"""Deterministic hard filters over the restaurant store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from src.preferences.schema import UserPreferences, validate_preferences

DEFAULT_TOP_N = 25

CANDIDATE_COLUMNS = (
    "name",
    "city",
    "city_display",
    "location",
    "location_raw",
    "cuisines_raw",
    "cuisine_tokens_str",
    "rating",
    "cost",
    "budget_band",
    "votes",
    "online_order",
    "book_table",
    "rest_type",
    "address",
    "url",
)


@dataclass(frozen=True)
class FilterResult:
    """Hard-filter output for downstream LLM / API layers."""

    candidates: pd.DataFrame
    match_count: int
    top_n: int
    preferences: UserPreferences

    @property
    def capped(self) -> bool:
        return self.match_count > len(self.candidates)

    @property
    def empty(self) -> bool:
        return self.candidates.empty

    def to_records(self) -> list[dict]:
        return self.candidates.to_dict(orient="records")


def default_top_n() -> int:
    return int(os.getenv("CANDIDATE_TOP_N", DEFAULT_TOP_N))


def _cuisine_tokens_from_row(token_str: object) -> set[str]:
    if token_str is None or (isinstance(token_str, float) and pd.isna(token_str)):
        return set()
    return {part.strip() for part in str(token_str).split(",") if part.strip()}


def _matches_location(df: pd.DataFrame, location_key: str) -> pd.Series:
    """Match city (e.g. Bangalore) or neighborhood/area (e.g. BTM)."""
    city_match = df["city"] == location_key
    area_match = df["location"] == location_key
    return city_match | area_match


def _matches_cuisine(df: pd.DataFrame, cuisine_tokens: tuple[str, ...]) -> pd.Series:
    """Any-match: restaurant matches if it shares at least one cuisine token."""
    requested = set(cuisine_tokens)

    def _row_matches(token_str: object) -> bool:
        return bool(requested & _cuisine_tokens_from_row(token_str))

    return df["cuisine_tokens_str"].map(_row_matches)


def _stable_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Deterministic ordering: rating ↓, votes ↓, name ↑ (F04)."""
    ordered = df.sort_values(
        by=["rating", "votes", "name"],
        ascending=[False, False, True],
        na_position="last",
        kind="mergesort",
    )
    return ordered.reset_index(drop=True)


def filter_candidates(
    preferences: UserPreferences,
    restaurants: pd.DataFrame,
    top_n: int | None = None,
) -> FilterResult:
    """Apply hard filters and return a capped candidate shortlist.

    Hard filters:
    - location → city OR area
    - cuisine → token any-match
    - min_rating → inclusive; unscored rows excluded
    - budget → exact budget_band match

    ``additional_preferences`` is intentionally not applied here (soft / LLM only).
    """
    if top_n is None:
        top_n = default_top_n()
    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    if restaurants is None or restaurants.empty:
        return FilterResult(
            candidates=pd.DataFrame(columns=list(CANDIDATE_COLUMNS)),
            match_count=0,
            top_n=top_n,
            preferences=preferences,
        )

    required = {"city", "location", "cuisine_tokens_str", "rating", "budget_band", "name"}
    missing = required - set(restaurants.columns)
    if missing:
        raise ValueError(f"Restaurant frame missing required columns: {sorted(missing)}")

    mask = (
        _matches_location(restaurants, preferences.location_key)
        & _matches_cuisine(restaurants, preferences.cuisine_tokens)
        & restaurants["budget_band"].eq(preferences.budget)
        & restaurants["rating"].notna()
        & (restaurants["rating"] >= preferences.min_rating)
    )

    matched = restaurants.loc[mask].copy()
    match_count = int(len(matched))
    ordered = _stable_sort(matched)
    capped = ordered.head(top_n).reset_index(drop=True)

    # Keep a stable column projection when columns exist
    keep = [c for c in CANDIDATE_COLUMNS if c in capped.columns]
    extras = [c for c in capped.columns if c not in keep]
    candidates = capped[keep + extras]

    return FilterResult(
        candidates=candidates,
        match_count=match_count,
        top_n=top_n,
        preferences=preferences,
    )


def get_candidates(
    raw_preferences: dict | UserPreferences,
    *,
    restaurants: Optional[pd.DataFrame] = None,
    top_n: int | None = None,
    store_path=None,
) -> FilterResult:
    """Validate preferences, load the store if needed, and hard-filter."""
    prefs = (
        raw_preferences
        if isinstance(raw_preferences, UserPreferences)
        else validate_preferences(raw_preferences)
    )
    if restaurants is None:
        from src.data.store import load_restaurants

        restaurants = load_restaurants(store_path)
    return filter_candidates(prefs, restaurants, top_n=top_n)
