"""Phase 1 tests for cleaning, ingest persistence, and store queries."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.ingest import (
    IngestError,
    assign_budget_bands,
    ingest,
    load_raw_dataframe,
    normalize_cuisine_tokens,
    parse_cost,
    parse_rating,
    transform_restaurants,
)
from src.data.store import StoreError, load_restaurants, query_restaurants

FIXTURE = Path(__file__).parent / "fixtures" / "zomato_sample.csv"


def test_parse_rating_variants():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("3.9 /5") == 3.9
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None
    assert parse_rating(None) is None


def test_parse_cost_with_commas():
    assert parse_cost("1,200") == 1200.0
    assert parse_cost("400") == 400.0
    assert parse_cost(None) is None


def test_normalize_cuisine_tokens():
    assert normalize_cuisine_tokens("Italian, Chinese") == ["italian", "chinese"]
    assert normalize_cuisine_tokens("NA") == []
    assert normalize_cuisine_tokens("") == []


def test_budget_bands_use_tertiles():
    costs = pd.Series([100.0, 200.0, 300.0, 400.0, 500.0, 600.0])
    bands, cutoffs = assign_budget_bands(costs)
    assert set(bands.dropna().unique()) <= {"low", "medium", "high"}
    assert cutoffs["low_max"] <= cutoffs["medium_max"]
    assert bands.iloc[0] == "low"
    assert bands.iloc[-1] == "high"


def test_transform_drops_nameless_and_dedupes():
    raw = load_raw_dataframe(FIXTURE)
    processed, meta = transform_restaurants(raw)

    assert meta["dropped_nameless"] >= 1
    assert meta["dropped_duplicates"] >= 1
    assert processed["name"].notna().all()
    # Higher-voted Epsilon Dup should win
    eps = processed[processed["name"] == "Epsilon Dup"]
    assert len(eps) == 1
    assert int(eps.iloc[0]["votes"]) == 80
    # Missing location becomes unknown
    assert "unknown" in set(processed["location"])
    # NEW / '-' ratings become null
    assert processed.loc[processed["name"] == "Gamma Cafe", "rating"].isna().all()
    assert processed.loc[processed["name"] == "Iota Bad Rate", "rating"].isna().all()


def test_schema_mismatch_fails_fast(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(IngestError, match="schema mismatch"):
        load_raw_dataframe(bad)


def test_ingest_and_query_roundtrip(tmp_path: Path):
    db_path = tmp_path / "restaurants.sqlite"
    meta = ingest(csv_path=FIXTURE, destination=db_path)

    assert db_path.exists()
    assert meta["processed_rows"] > 0

    df = load_restaurants(db_path)
    assert not df.empty
    assert "budget_band" in df.columns

    italian = query_restaurants(city="Bangalore", cuisine="Italian", path=db_path, limit=10)
    assert len(italian) >= 1
    assert all("italian" in str(x) for x in italian["cuisine_tokens_str"])

    # min_rating excludes unscored rows
    rated = query_restaurants(city="Bangalore", min_rating=4.0, path=db_path, limit=50)
    assert rated["rating"].notna().all()
    assert (rated["rating"] >= 4.0).all()


def test_missing_store_guidance(tmp_path: Path):
    missing = tmp_path / "missing.sqlite"
    with pytest.raises(StoreError, match="python -m src.data.ingest"):
        load_restaurants(missing)
