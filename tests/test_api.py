"""Phase 4 API and orchestration tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.routes import create_app
from src.data.ingest import ingest
from src.data.store import load_restaurants
from src.filtering import get_candidates
from src.llm.client import LLMClient, LLMError
from src.llm.config import LLMConfig
from src.preferences.schema import PreferenceValidationError
from src.recommend.engine import recommend

FIXTURE = Path(__file__).parent / "fixtures" / "zomato_sample.csv"


@pytest.fixture
def sample_store(tmp_path: Path):
    db_path = tmp_path / "restaurants.sqlite"
    ingest(csv_path=FIXTURE, destination=db_path)
    return load_restaurants(db_path)


@pytest.fixture
def client():
    return TestClient(create_app())


def _mock_llm(name: str) -> MagicMock:
    mock = MagicMock(spec=LLMClient)
    mock.config = LLMConfig(
        api_key="test",
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b",
    )
    mock.complete.return_value = (
        '{"summary":"API picks","recommendations":['
        f'{{"restaurant_name":"{name}","explanation":"Great match."}}'
        "]}"
    )
    return mock


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_recommend_validation_error(client: TestClient):
    res = client.post("/recommend", json={"location": "Bangalore"})
    assert res.status_code == 422
    body = res.json()
    assert body["error"] == "validation_error"


def test_recommend_invalid_preferences_maps_to_400(client: TestClient):
    with patch(
        "src.api.routes.recommend",
        side_effect=PreferenceValidationError("Invalid budget 'luxury'"),
    ):
        res = client.post(
            "/recommend",
            json={
                "location": "Bangalore",
                "budget": "luxury",
                "cuisine": "Italian",
                "min_rating": 4.0,
            },
        )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_preferences"


def test_recommend_success_with_mocked_engine(client: TestClient):
    payload = {
        "summary": "Top picks",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": "Onesta",
                "cuisine": "Italian",
                "rating": 4.6,
                "estimated_cost": "medium",
                "explanation": "Great family option.",
                "location": "HSR",
                "cost_for_two": 600.0,
            }
        ],
        "meta": {
            "candidates_considered": 5,
            "used_fallback": False,
            "match_count": 10,
            "no_matches": False,
            "capped": True,
            "status": "ok",
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
        },
    }
    with patch("src.api.routes.recommend", return_value=payload):
        res = client.post(
            "/recommend",
            json={
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": "family-friendly",
                "extra_ignored_field": True,
            },
        )
    assert res.status_code == 200
    data = res.json()
    assert data["recommendations"][0]["restaurant_name"] == "Onesta"
    assert data["meta"]["status"] == "ok"
    assert data["meta"]["used_fallback"] is False


def test_engine_no_matches_status(sample_store):
    result = recommend(
        {
            "location": "Atlantis",
            "budget": "low",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
        restaurants=sample_store,
        client=_mock_llm("x"),
    )
    assert result["meta"]["status"] == "no_matches"
    assert result["meta"]["no_matches"] is True
    assert result["recommendations"] == []


def test_engine_ok_and_fallback_status(sample_store):
    prefs = {
        "location": "Bangalore",
        "budget": "high",
        "cuisine": "Italian",
        "min_rating": 4.0,
    }
    candidates = get_candidates(prefs, restaurants=sample_store, top_n=3).candidates
    name = candidates.iloc[0]["name"]

    ok = recommend(prefs, restaurants=sample_store, top_n=3, client=_mock_llm(name))
    assert ok["meta"]["status"] == "ok"
    assert ok["meta"]["used_fallback"] is False
    assert ok["recommendations"][0]["restaurant_name"] == name

    mock = _mock_llm(name)
    mock.complete.side_effect = LLMError("timeout")
    fb = recommend(prefs, restaurants=sample_store, top_n=3, client=mock)
    assert fb["meta"]["status"] == "llm_fallback"
    assert fb["meta"]["used_fallback"] is True
