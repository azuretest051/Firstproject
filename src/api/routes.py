"""FastAPI routes for the restaurant recommendation service."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.schemas import (
    ErrorResponse,
    RecommendRequest,
    RecommendResponse,
)
from src.data.paths import PROCESSED_DB_PATH
from src.data.store import StoreError, list_cities, list_locations
from src.preferences.schema import PreferenceValidationError
from src.recommend.engine import recommend

logger = logging.getLogger(__name__)

_WEB_DIR = Path(__file__).resolve().parents[1] / "ui" / "web"


def _cors_origins() -> list[str]:
    """Parse CORS_ORIGINS (comma-separated). Default * for free-tier demos."""
    raw = (os.getenv("CORS_ORIGINS") or "*").strip()
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


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

    origins = _cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
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
    def health() -> dict[str, Any]:
        """Liveness for Railway / load balancers; reports SQLite presence."""
        store_ready = PROCESSED_DB_PATH.is_file()
        payload: dict[str, Any] = {
            "status": "ok" if store_ready else "degraded",
            "store_ready": store_ready,
        }
        if not store_ready:
            payload["detail"] = (
                f"Processed store missing at {PROCESSED_DB_PATH}. "
                "Ship data/processed/restaurants.sqlite or set PROCESSED_DATA_PATH."
            )
        return payload

    @app.get("/meta/locations")
    def meta_locations() -> dict[str, Any]:
        """City + neighborhood options for the Stitch preference form."""
        try:
            cities = list_cities()
            locations = list_locations()
        except StoreError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"cities": cities, "locations": locations}

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

    # Stitch-faithful TasteMatch UI (desktop home + desktop results).
    if _WEB_DIR.is_dir():
        js_dir = _WEB_DIR / "js"
        if js_dir.is_dir():
            app.mount("/js", StaticFiles(directory=str(js_dir)), name="tm-js")

        @app.get("/")
        def ui_home() -> FileResponse:
            return FileResponse(_WEB_DIR / "index.html")

        @app.get("/results.html")
        def ui_results() -> FileResponse:
            return FileResponse(_WEB_DIR / "results.html")

    return app


# ASGI app for `uvicorn src.api.routes:app`
app = create_app()
