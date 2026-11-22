"""FastAPI routes for the restaurant recommendation service."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.schemas import (
    ErrorResponse,
    RecommendRequest,
    RecommendResponse,
)
from src.data.store import StoreError
from src.preferences.schema import PreferenceValidationError
from src.recommend.engine import recommend

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and return the FastAPI application."""
    app = FastAPI(
        title="Restaurant Recommendation API",
        description=(
            "AI-powered Zomato-style recommendations: "
            "hard filters + Groq LLM ranking/explanations."
        ),
        version="0.1.0",
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(PreferenceValidationError)
    async def preference_validation_handler(
        request: Request, exc: PreferenceValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_preferences", "detail": str(exc)},
        )

    @app.exception_handler(StoreError)
    async def store_error_handler(request: Request, exc: StoreError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"error": "store_unavailable", "detail": str(exc)},
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/recommend",
        response_model=RecommendResponse,
        responses={
            400: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            500: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
        },
    )
    def post_recommend(body: RecommendRequest) -> dict[str, Any]:
        """Run validate → filter → Groq rank and return structured recommendations."""
        prefs = body.model_dump(exclude={"top_n"}, exclude_none=False)
        try:
            return recommend(prefs, top_n=body.top_n)
        except PreferenceValidationError:
            raise
        except StoreError:
            raise
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Recommend endpoint failed")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while generating recommendations.",
            ) from exc

    return app


# ASGI app for `uvicorn src.api.routes:app`
app = create_app()
