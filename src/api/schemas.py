"""Pydantic request/response models for the recommendation API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RecommendRequest(BaseModel):
    """User preference payload for POST /recommend."""

    model_config = ConfigDict(extra="ignore")  # A02: ignore unknown fields

    location: str = Field(..., min_length=1, examples=["Bangalore"])
    budget: str = Field(..., examples=["medium"])
    cuisine: str = Field(..., examples=["Italian"])
    min_rating: float = Field(..., ge=0, le=5, examples=[4.0])
    additional_preferences: Optional[str] = Field(
        default=None,
        examples=["family-friendly, outdoor seating"],
    )
    top_n: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
        description="Optional override for candidate shortlist size.",
    )


class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    rank: int
    restaurant_name: str
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    estimated_cost: Optional[str] = None
    explanation: str
    location: Optional[str] = None
    cost_for_two: Optional[float] = None


class RecommendMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    candidates_considered: int = 0
    used_fallback: bool = False
    match_count: int = 0
    no_matches: bool = False
    capped: bool = False
    status: str = "ok"
    provider: Optional[str] = None
    model: Optional[str] = None
    fallback_reason: Optional[str] = None


class RecommendResponse(BaseModel):
    summary: str
    recommendations: list[RecommendationItem]
    meta: RecommendMeta


class ErrorResponse(BaseModel):
    error: str
    detail: Any = None
