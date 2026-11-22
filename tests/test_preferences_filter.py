"""Phase 2 tests for preference validation and hard filtering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.ingest import ingest
from src.data.store import load_restaurants
from src.filtering.filter import filter_candidates, get_candidates
from src.preferences.schema import PreferenceValidationError, validate_preferences

FIXTURE = Path(__file__).parent / "fixtures" / "zomato_sample.csv"


@pytest.fixture
def sample_store(tmp_path: Path) -> pd.DataFrame:
    db_path = tmp_path / "restaurants.sqlite"
    ingest(csv_path=FIXTURE, destination=db_path)
    return load_restaurants(db_path)


def test_validate_preferences_normalizes_fields():
    prefs = validate_preferences(
        {
            "location": "  Bangalore ",
            "budget": "MEDIUM",
            "cuisine": "Italian, Chinese",
            "min_rating": "4.0",
            "additional_preferences": "  family-friendly  ",
        }
    )
    assert prefs.location_key == "bangalore"
    assert prefs.budget == "medium"
    assert prefs.cuisine_tokens == ("italian", "chinese")
    assert prefs.min_rating == 4.0
    assert prefs.additional_preferences == "family-friendly"


@pytest.mark.parametrize(
    "raw,match",
    [
        ({}, "location"),
        ({"location": " ", "budget": "low", "cuisine": "Italian", "min_rating": 4}, "location"),
        (
            {"location": "BTM", "budget": "cheap", "cuisine": "Italian", "min_rating": 4},
            "budget",
        ),
        (
            {"location": "BTM", "budget": "low", "cuisine": "Italian", "min_rating": 6},
            "min_rating",
        ),
        (
            {"location": "BTM", "budget": "low", "cuisine": "Italian", "min_rating": "NaN"},
            "min_rating",
        ),
        (
            {"location": "BTM", "budget": "low", "cuisine": "   ", "min_rating": 4},
            "cuisine",
        ),
    ],
)
def test_validate_preferences_rejects_invalid(raw, match):
    with pytest.raises(PreferenceValidationError, match=match):
        validate_preferences(raw)


def test_additional_preferences_optional_and_truncated():
    prefs = validate_preferences(
        {
            "location": "Bangalore",
            "budget": "low",
            "cuisine": "Cafe",
            "min_rating": 0,
        }
    )
    assert prefs.additional_preferences is None

    long_text = "x" * 800
    prefs2 = validate_preferences(
        {
            "location": "Bangalore",
            "budget": "low",
            "cuisine": "Cafe",
            "min_rating": 0,
            "additional_preferences": long_text,
        }
    )
    assert prefs2.additional_preferences is not None
    assert len(prefs2.additional_preferences) == 500


def test_filter_city_cuisine_budget_and_boundary_rating(sample_store: pd.DataFrame):
    prefs = validate_preferences(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisine": "italian",
            "min_rating": 4.5,
        }
    )
    result = filter_candidates(prefs, sample_store, top_n=10)

    assert result.match_count >= 1
    assert not result.empty
    assert (result.candidates["budget_band"] == "high").all()
    assert (result.candidates["rating"] >= 4.5).all()
    assert all(
        "italian" in str(tokens)
        for tokens in result.candidates["cuisine_tokens_str"]
    )


def test_filter_area_location_and_any_match_cuisine(sample_store: pd.DataFrame):
    # Epsilon Dup has Chinese, Thai — requesting Thai should match (any-match / F06)
    prefs = validate_preferences(
        {
            "location": "BTM",
            "budget": "medium",
            "cuisine": "Thai",
            "min_rating": 4.0,
        }
    )
    result = filter_candidates(prefs, sample_store, top_n=10)
    assert result.match_count == 1
    assert result.candidates.iloc[0]["name"] == "Epsilon Dup"


def test_filter_inclusive_rating_boundary(sample_store: pd.DataFrame):
    prefs = validate_preferences(
        {
            "location": "BTM",
            "budget": "medium",
            "cuisine": "Chinese",
            "min_rating": 4.2,
        }
    )
    result = filter_candidates(prefs, sample_store, top_n=10)
    assert not result.empty
    assert (result.candidates["rating"] >= 4.2).all()
    # Exact boundary row included
    assert (result.candidates["rating"] == 4.2).any()


def test_filter_excludes_unscored_when_min_rating_set(sample_store: pd.DataFrame):
    prefs = validate_preferences(
        {
            "location": "Bangalore",
            "budget": "low",
            "cuisine": "Cafe",
            "min_rating": 0.0,
        }
    )
    result = filter_candidates(prefs, sample_store, top_n=25)
    # Gamma Cafe is NEW/unscored and must be excluded when min_rating is set
    assert "Gamma Cafe" not in set(result.candidates["name"])


def test_filter_no_matches_and_top_n_cap(sample_store: pd.DataFrame):
    empty = filter_candidates(
        validate_preferences(
            {
                "location": "Atlantis",
                "budget": "low",
                "cuisine": "Italian",
                "min_rating": 4.0,
            }
        ),
        sample_store,
        top_n=5,
    )
    assert empty.empty
    assert empty.match_count == 0

    many = filter_candidates(
        validate_preferences(
            {
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "Chinese",
                "min_rating": 0.0,
            }
        ),
        sample_store,
        top_n=1,
    )
    assert many.match_count >= 1
    assert len(many.candidates) == 1
    assert many.capped is (many.match_count > 1)


def test_filter_ignores_additional_preferences(sample_store: pd.DataFrame):
    base = {
        "location": "Bangalore",
        "budget": "high",
        "cuisine": "Italian",
        "min_rating": 4.0,
    }
    without = filter_candidates(validate_preferences(base), sample_store, top_n=10)
    with_soft = filter_candidates(
        validate_preferences({**base, "additional_preferences": "rooftop only"}),
        sample_store,
        top_n=10,
    )
    assert list(without.candidates["name"]) == list(with_soft.candidates["name"])


def test_get_candidates_end_to_end(sample_store: pd.DataFrame):
    result = get_candidates(
        {
            "location": "indiranagar",
            "budget": "high",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_preferences": "romantic",
        },
        restaurants=sample_store,
        top_n=5,
    )
    assert not result.empty
    row = result.candidates.iloc[0]
    for col in ("name", "cuisines_raw", "rating", "cost", "budget_band"):
        assert col in row
    assert result.preferences.additional_preferences == "romantic"


def test_sort_is_deterministic_with_ties():
    df = pd.DataFrame(
        [
            {
                "name": "B Place",
                "city": "bangalore",
                "location": "btm",
                "cuisine_tokens_str": "italian",
                "rating": 4.0,
                "votes": 10,
                "budget_band": "medium",
                "cost": 500,
            },
            {
                "name": "A Place",
                "city": "bangalore",
                "location": "btm",
                "cuisine_tokens_str": "italian",
                "rating": 4.0,
                "votes": 10,
                "budget_band": "medium",
                "cost": 500,
            },
        ]
    )
    prefs = validate_preferences(
        {
            "location": "BTM",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    first = filter_candidates(prefs, df, top_n=10)
    second = filter_candidates(prefs, df, top_n=10)
    assert list(first.candidates["name"]) == ["A Place", "B Place"]
    assert list(second.candidates["name"]) == list(first.candidates["name"])
