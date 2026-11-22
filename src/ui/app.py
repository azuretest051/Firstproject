"""Streamlit UI: preference form → recommend engine → ranked results."""

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any, Optional

import streamlit as st

# Allow `streamlit run src/ui/app.py` from the repo root without installing the package.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data.store import StoreError, list_cities, list_locations, load_restaurants
from src.preferences.schema import PreferenceValidationError
from src.recommend import recommend

PAGE_TITLE = "Restaurant Recommendations"
COMMON_CUISINES = [
    "North Indian",
    "Chinese",
    "South Indian",
    "Fast Food",
    "Biryani",
    "Italian",
    "Cafe",
    "Continental",
    "Pizza",
    "Street Food",
]


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 960px; }
          .rec-card {
            border: 1px solid #e2e5ea;
            border-radius: 12px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.85rem;
            background: #ffffff;
          }
          .rec-rank {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #5b6472;
            margin-bottom: 0.35rem;
          }
          .rec-name {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1a1f2b;
            margin: 0 0 0.35rem 0;
          }
          .rec-meta {
            color: #5b6472;
            font-size: 0.92rem;
            margin-bottom: 0.55rem;
          }
          .rec-explain {
            color: #2c3340;
            font-size: 0.95rem;
            line-height: 1.45;
            margin: 0;
          }
          .summary-box {
            border-left: 4px solid #2f6fed;
            background: #f4f7fc;
            padding: 0.85rem 1rem;
            border-radius: 0 8px 8px 0;
            margin: 0.5rem 0 1.1rem 0;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _cached_cities() -> list[str]:
    return list_cities()


@st.cache_data(show_spinner=False)
def _cached_locations(city: Optional[str] = None) -> list[str]:
    return list_locations(city=city)


@st.cache_data(show_spinner=False)
def _store_ready() -> tuple[bool, str]:
    try:
        df = load_restaurants()
        return True, f"{len(df):,} restaurants loaded"
    except StoreError as exc:
        return False, str(exc)


def _format_meta_line(item: dict[str, Any]) -> str:
    parts: list[str] = []
    cuisine = item.get("cuisine")
    if cuisine:
        parts.append(str(cuisine))
    rating = item.get("rating")
    if rating is not None:
        parts.append(f"Rating {rating}")
    cost = item.get("estimated_cost") or item.get("cost_for_two")
    if cost is not None and cost != "":
        if isinstance(cost, (int, float)):
            parts.append(f"₹{int(cost)} for two")
        else:
            parts.append(f"Budget: {cost}")
    location = item.get("location")
    if location:
        parts.append(str(location))
    return " · ".join(parts)


def _render_recommendation(item: dict[str, Any]) -> None:
    rank = _esc(item.get("rank", "?"))
    name = _esc(item.get("restaurant_name") or "Unknown restaurant")
    explanation = _esc(item.get("explanation") or "No explanation provided.")
    meta = _esc(_format_meta_line(item))
    st.markdown(
        f"""
        <div class="rec-card">
          <div class="rec-rank">#{rank}</div>
          <p class="rec-name">{name}</p>
          <div class="rec-meta">{meta}</div>
          <p class="rec-explain">{explanation}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_banner(meta: dict[str, Any]) -> None:
    status = meta.get("status", "ok")
    considered = meta.get("candidates_considered", 0)
    match_count = meta.get("match_count", 0)

    if status == "no_matches":
        st.warning(
            "No restaurants matched your filters. "
            "Try a broader location, different cuisine, higher budget, or lower minimum rating."
        )
        return

    if status == "llm_fallback":
        reason = meta.get("fallback_reason")
        msg = (
            "AI ranking was unavailable — showing rating-sorted matches instead."
        )
        if reason:
            msg += f" ({reason})"
        st.info(msg)

    caps = f"{considered} shortlisted"
    if meta.get("capped") and match_count:
        caps = f"{considered} of {match_count} matches shortlisted"
    st.caption(
        f"Status: {status} · {caps}"
        + (f" · model: {meta['model']}" if meta.get("model") else "")
    )


def _build_location_options() -> list[str]:
    cities = _cached_cities()
    locations = _cached_locations()
    # City-wide first, then neighborhoods — filter accepts either.
    options: list[str] = []
    for city in cities:
        if city not in options:
            options.append(city)
    for loc in locations:
        if loc not in options:
            options.append(loc)
    return options


def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE,
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_styles()

    st.title(PAGE_TITLE)
    st.caption(
        "Hard filters narrow the Zomato catalog; an LLM ranks the shortlist and explains each pick."
    )

    ready, store_msg = _store_ready()
    if not ready:
        st.error(store_msg)
        st.stop()
    st.caption(store_msg)

    location_options = _build_location_options()
    default_location = "Bangalore" if "Bangalore" in location_options else location_options[0]

    with st.form("preferences_form", clear_on_submit=False):
        st.subheader("Your preferences")

        col1, col2 = st.columns(2)
        with col1:
            location_mode = st.radio(
                "Location mode",
                options=["Pick from list", "Type custom"],
                horizontal=True,
                help="City-wide (e.g. Bangalore) or a neighborhood (e.g. BTM).",
            )
            if location_mode == "Pick from list":
                location = st.selectbox(
                    "Location",
                    options=location_options,
                    index=location_options.index(default_location),
                )
            else:
                location = st.text_input(
                    "Location",
                    value=default_location,
                    placeholder="Bangalore or BTM",
                )

            cuisine = st.selectbox(
                "Cuisine",
                options=COMMON_CUISINES + ["Other…"],
                index=COMMON_CUISINES.index("Italian")
                if "Italian" in COMMON_CUISINES
                else 0,
            )
            if cuisine == "Other…":
                cuisine = st.text_input(
                    "Custom cuisine",
                    placeholder="e.g. Japanese, Kerala",
                )

        with col2:
            budget = st.selectbox(
                "Budget",
                options=["low", "medium", "high"],
                index=1,
                help="Mapped from approximate cost for two.",
            )
            min_rating = st.slider(
                "Minimum rating",
                min_value=0.0,
                max_value=5.0,
                value=4.0,
                step=0.1,
            )

        additional_preferences = st.text_area(
            "Additional preferences (optional)",
            placeholder="family-friendly, outdoor seating, quick service…",
            height=80,
            help="Soft hints for the LLM — not applied as hard filters.",
        )

        submitted = st.form_submit_button(
            "Get recommendations",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    prefs = {
        "location": (location or "").strip(),
        "budget": budget,
        "cuisine": (cuisine or "").strip(),
        "min_rating": float(min_rating),
        "additional_preferences": (additional_preferences or "").strip() or None,
    }

    with st.spinner("Filtering restaurants and ranking with the LLM…"):
        try:
            result = recommend(prefs)
        except PreferenceValidationError as exc:
            st.error(f"Invalid preferences: {exc}")
            return
        except StoreError as exc:
            st.error(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"Something went wrong: {exc}")
            return

    st.subheader("Results")
    meta = result.get("meta") or {}
    _status_banner(meta)

    summary = (result.get("summary") or "").strip()
    if summary:
        st.markdown(
            f'<div class="summary-box">{_esc(summary)}</div>',
            unsafe_allow_html=True,
        )

    recommendations = result.get("recommendations") or []
    if not recommendations:
        return

    for item in recommendations:
        if isinstance(item, dict):
            _render_recommendation(item)


if __name__ == "__main__":
    main()
