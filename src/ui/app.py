"""TasteMatch AI — Streamlit entrypoint.

The Stitch-faithful UI is the FastAPI-hosted web app under ``src/ui/web/``.
Streamlit remains available as a lightweight fallback form.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data.store import StoreError, list_cities, list_locations, load_restaurants
from src.preferences.schema import PreferenceValidationError
from src.recommend import recommend

PAGE_TITLE = "TasteMatch AI"
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


@st.cache_data(show_spinner=False)
def _store_ready() -> tuple[bool, str]:
    try:
        df = load_restaurants()
        return True, f"{len(df):,} restaurants loaded"
    except StoreError as exc:
        return False, str(exc)


@st.cache_data(show_spinner=False)
def _location_options() -> list[str]:
    options: list[str] = []
    for city in list_cities():
        if city not in options:
            options.append(city)
    for loc in list_locations():
        if loc not in options:
            options.append(loc)
    return options


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="🔥", layout="centered")
    st.title("TasteMatch AI")
    st.info(
        "For the full Stitch desktop UI (home + results), run the API and open "
        "**http://127.0.0.1:8000/** — "
        "`python -m uvicorn src.api.routes:app --reload --host 127.0.0.1 --port 8000`"
    )

    ready, store_msg = _store_ready()
    if not ready:
        st.error(store_msg)
        st.stop()
    st.caption(store_msg)

    options = _location_options()
    if not options:
        st.error("No locations available in the restaurant store.")
        st.stop()
    default = "Bangalore" if "Bangalore" in options else options[0]

    with st.form("prefs"):
        location = st.selectbox("Location", options=options, index=options.index(default))
        cuisine = st.selectbox("Cuisine", options=COMMON_CUISINES, index=0)
        budget = st.selectbox("Budget", options=["low", "medium", "high"], index=1)
        min_rating = st.slider("Minimum rating", 0.0, 5.0, 4.0, 0.1)
        extra = st.text_area("Additional preferences (optional)", height=80)
        submitted = st.form_submit_button("Get recommendations", type="primary")

    if not submitted:
        return

    prefs = {
        "location": location.strip(),
        "budget": budget,
        "cuisine": cuisine.strip(),
        "min_rating": float(min_rating),
        "additional_preferences": (extra or "").strip() or None,
    }
    with st.spinner("Evaluating kitchens…"):
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

    meta = result.get("meta") or {}
    if meta.get("status") == "llm_fallback":
        st.warning("AI ranking unavailable — showing rating-sorted matches.")

    summary = (result.get("summary") or "").strip()
    if summary:
        st.write(summary)

    recs = [r for r in (result.get("recommendations") or []) if isinstance(r, dict)]
    if not recs:
        st.warning("No matches for these preferences. Try widening filters.")
        return

    for item in recs:
        with st.container(border=True):
            st.subheader(f"#{item.get('rank', '—')} · {item.get('restaurant_name', 'Unknown')}")
            st.caption(
                f"{item.get('cuisine') or '—'} · ★ {item.get('rating') or '—'} · "
                f"{item.get('estimated_cost') or item.get('cost_for_two') or '—'}"
            )
            st.write(item.get("explanation") or "")


if __name__ == "__main__":
    main()
