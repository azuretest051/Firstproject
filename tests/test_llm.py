"""Phase 3 tests for Groq prompt/parser/ranker (mocked network)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.data.ingest import ingest
from src.data.store import load_restaurants
from src.filtering import get_candidates
from src.llm.client import LLMClient, LLMError
from src.llm.config import LLMConfig, LLMConfigError
from src.llm.parser import (
    ParseError,
    extract_json_object,
    fallback_recommendations,
    parse_recommendations,
)
from src.llm.prompt import build_recommendation_prompt
from src.llm.ranker import rank_candidates
from src.preferences.schema import validate_preferences
from src.recommend.engine import recommend

FIXTURE = Path(__file__).parent / "fixtures" / "zomato_sample.csv"


@pytest.fixture
def sample_store(tmp_path: Path) -> pd.DataFrame:
    db_path = tmp_path / "restaurants.sqlite"
    ingest(csv_path=FIXTURE, destination=db_path)
    return load_restaurants(db_path)


@pytest.fixture
def prefs_and_candidates(sample_store: pd.DataFrame):
    prefs = validate_preferences(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisine": "Italian",
            "min_rating": 4.0,
            "additional_preferences": "family-friendly",
        }
    )
    filtered = get_candidates(prefs, restaurants=sample_store, top_n=5)
    return prefs, filtered.candidates


def test_extract_json_strips_markdown_fence():
    raw = """```json
{"summary": "ok", "recommendations": []}
```"""
    data = extract_json_object(raw)
    assert data["summary"] == "ok"


def test_parse_grounds_to_candidates_and_prefers_store_fields(prefs_and_candidates):
    prefs, candidates = prefs_and_candidates
    assert not candidates.empty
    name = candidates.iloc[0]["name"]
    raw = {
        "summary": "Great picks",
        "recommendations": [
            {
                "rank": 1,
                "restaurant_name": name,
                "cuisine": "FAKE CUISINE",
                "rating": 1.0,
                "estimated_cost": "low",
                "explanation": "Good fit for Italian night.",
            },
            {
                "rank": 2,
                "restaurant_name": "Totally Invented Place",
                "cuisine": "Martian",
                "rating": 5.0,
                "estimated_cost": "high",
                "explanation": "Hallucination",
            },
        ],
    }
    import json

    parsed = parse_recommendations(json.dumps(raw), candidates)
    assert len(parsed["recommendations"]) == 1
    rec = parsed["recommendations"][0]
    assert rec["restaurant_name"] == name
    assert rec["cuisine"] == candidates.iloc[0]["cuisines_raw"]
    assert rec["rating"] == candidates.iloc[0]["rating"]
    assert rec["estimated_cost"] == candidates.iloc[0]["budget_band"]
    assert "Italian" in rec["explanation"] or "fit" in rec["explanation"].lower()
    assert parsed["meta"]["used_fallback"] is False


def test_parse_rejects_ungrounded_only_output(prefs_and_candidates):
    _, candidates = prefs_and_candidates
    raw = """
    {"summary": "x", "recommendations": [
      {"restaurant_name": "No Such Place", "explanation": "nope"}
    ]}
    """
    with pytest.raises(ParseError, match="grounded"):
        parse_recommendations(raw, candidates)


def test_fallback_recommendations_flags_meta(prefs_and_candidates):
    _, candidates = prefs_and_candidates
    result = fallback_recommendations(candidates, reason="timeout")
    assert result["meta"]["used_fallback"] is True
    assert result["meta"]["fallback_reason"] == "timeout"
    assert result["recommendations"]
    assert "AI ranking unavailable" in result["recommendations"][0]["explanation"]


def test_prompt_includes_prefs_and_candidates(prefs_and_candidates):
    prefs, candidates = prefs_and_candidates
    prompt = build_recommendation_prompt(prefs, candidates)
    assert "family-friendly" in prompt
    assert candidates.iloc[0]["name"] in prompt
    assert "JSON" in prompt or "json" in prompt


def test_rank_candidates_uses_llm_when_available(prefs_and_candidates):
    prefs, candidates = prefs_and_candidates
    name = candidates.iloc[0]["name"]
    mock_client = MagicMock(spec=LLMClient)
    mock_client.config = LLMConfig(
        api_key="test",
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    )
    mock_client.complete.return_value = f"""
    {{
      "summary": "Top Italian picks",
      "recommendations": [
        {{
          "rank": 1,
          "restaurant_name": "{name}",
          "cuisine": "Italian",
          "rating": 4.5,
          "estimated_cost": "high",
          "explanation": "Strong Italian match in budget."
        }}
      ]
    }}
    """
    result = rank_candidates(prefs, candidates, client=mock_client)
    assert result["meta"]["used_fallback"] is False
    assert result["recommendations"][0]["restaurant_name"] == name
    mock_client.complete.assert_called()


def test_rank_candidates_falls_back_on_llm_error(prefs_and_candidates):
    prefs, candidates = prefs_and_candidates
    mock_client = MagicMock(spec=LLMClient)
    mock_client.config = LLMConfig(
        api_key="test",
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    )
    mock_client.complete.side_effect = LLMError("boom")
    result = rank_candidates(prefs, candidates, client=mock_client)
    assert result["meta"]["used_fallback"] is True
    assert len(result["recommendations"]) == len(candidates)


def test_recommend_no_matches(sample_store: pd.DataFrame):
    result = recommend(
        {
            "location": "Atlantis",
            "budget": "low",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
        restaurants=sample_store,
        client=MagicMock(spec=LLMClient),
    )
    assert result["meta"]["no_matches"] is True
    assert result["recommendations"] == []


def test_recommend_end_to_end_with_mock_groq(sample_store: pd.DataFrame):
    filtered = get_candidates(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
        restaurants=sample_store,
        top_n=3,
    )
    name = filtered.candidates.iloc[0]["name"]
    mock_client = MagicMock(spec=LLMClient)
    mock_client.config = LLMConfig(
        api_key="test",
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    )
    mock_client.complete.return_value = (
        '{"summary":"ok","recommendations":['
        f'{{"restaurant_name":"{name}","explanation":"Fits well."}}'
        "]}"
    )
    result = recommend(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
        restaurants=sample_store,
        top_n=3,
        client=mock_client,
    )
    assert result["recommendations"][0]["restaurant_name"] == name
    assert "explanation" in result["recommendations"][0]
    assert result["meta"]["used_fallback"] is False
    assert result["meta"]["candidates_considered"] == len(filtered.candidates)


def test_missing_api_key_config(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    from src.llm.config import load_llm_config

    with pytest.raises(LLMConfigError, match="GROQ_API_KEY"):
        load_llm_config()
