"""Read and query the processed restaurant store."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

from src.data.paths import PROCESSED_DB_PATH, RESTAURANTS_TABLE


class StoreError(RuntimeError):
    """Raised when the processed store cannot be loaded or queried."""


def _resolve_db_path(path: Path | None = None) -> Path:
    db_path = path or PROCESSED_DB_PATH
    if db_path.suffix.lower() in {".parquet", ".csv"}:
        candidate = db_path.with_suffix(".sqlite")
        if candidate.exists():
            return candidate
    return db_path


def load_restaurants(path: Path | None = None) -> pd.DataFrame:
    """Load processed restaurant records from SQLite.

    Raises ``StoreError`` with setup guidance when the store is missing
    or unreadable (edge case D11).
    """
    db_path = _resolve_db_path(path)
    if not db_path.exists():
        raise StoreError(
            f"Processed restaurant store not found at {db_path}. "
            "Run: python -m src.data.ingest"
        )

    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {RESTAURANTS_TABLE}", conn)
    except Exception as exc:  # noqa: BLE001
        raise StoreError(
            f"Failed to read restaurant store at {db_path}: {exc}. "
            "Re-run: python -m src.data.ingest"
        ) from exc

    if df.empty:
        raise StoreError(
            f"Restaurant store at {db_path} is empty. "
            "Re-run: python -m src.data.ingest"
        )
    return df


def _normalize_query_token(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def query_restaurants(
    *,
    city: Optional[str] = None,
    location: Optional[str] = None,
    cuisine: Optional[str] = None,
    budget: Optional[str] = None,
    min_rating: Optional[float] = None,
    limit: Optional[int] = 10,
    path: Path | None = None,
) -> pd.DataFrame:
    """Filter processed restaurants by common fields.

    Cuisine matching is token-based (any-match): a restaurant matches if
    any of its cuisine tokens equals the requested cuisine (casefold).
    """
    df = load_restaurants(path)
    result = df

    if city:
        city_key = _normalize_query_token(city)
        result = result[result["city"] == city_key]

    if location:
        location_key = _normalize_query_token(location)
        result = result[result["location"] == location_key]

    if cuisine:
        cuisine_key = _normalize_query_token(cuisine)

        def _has_cuisine(token_str: object) -> bool:
            if token_str is None or (isinstance(token_str, float) and pd.isna(token_str)):
                return False
            tokens = [t.strip() for t in str(token_str).split(",") if t.strip()]
            return cuisine_key in tokens

        result = result[result["cuisine_tokens_str"].map(_has_cuisine)]

    if budget:
        budget_key = _normalize_query_token(budget)
        if budget_key not in {"low", "medium", "high"}:
            raise ValueError("budget must be one of: low, medium, high")
        result = result[result["budget_band"] == budget_key]

    if min_rating is not None:
        # Unscored rows (null rating) are excluded when a min is set (D05)
        result = result[result["rating"].notna() & (result["rating"] >= float(min_rating))]

    result = result.sort_values(
        by=["rating", "votes"],
        ascending=[False, False],
        na_position="last",
    )

    if limit is not None:
        result = result.head(int(limit))

    return result.reset_index(drop=True)


def list_cities(path: Path | None = None) -> list[str]:
    """Return available display city values."""
    df = load_restaurants(path)
    return sorted(df["city_display"].dropna().unique().tolist())


def list_locations(path: Path | None = None, *, city: Optional[str] = None) -> list[str]:
    """Return available display location/area values."""
    df = load_restaurants(path)
    if city:
        city_key = _normalize_query_token(city)
        df = df[df["city"] == city_key]
    return sorted(df["location_raw"].dropna().unique().tolist())


def sample_by_city_cuisine(
    city: str,
    cuisine: str,
    *,
    limit: int = 5,
    path: Path | None = None,
) -> pd.DataFrame:
    """Convenience helper for Phase 1 exit criteria demos."""
    return query_restaurants(city=city, cuisine=cuisine, limit=limit, path=path)
