"""Load and preprocess the Zomato dataset from Hugging Face.

Downloads ``zomato.csv``, cleans product fields, derives budget bands,
dedupes restaurants, and atomically persists a SQLite store under
``data/processed/``.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import tempfile
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

from src.data.paths import (
    HF_CSV_FILENAME,
    HF_DATASET_ID,
    PROCESSED_DB_PATH,
    PROCESSED_DIR,
    RAW_CSV_PATH,
    RAW_DIR,
    REQUIRED_SOURCE_COLUMNS,
    RESTAURANTS_TABLE,
)

logger = logging.getLogger(__name__)

# Dataset is Bangalore-focused Zomato listings.
DEFAULT_CITY = "Bangalore"

_NA_CUISINE_TOKENS = {"", "na", "n/a", "none", "nan", "null"}
_UNSCORED_RATINGS = {"", "-", "new", "nan", "null"}


class IngestError(RuntimeError):
    """Raised when ingestion cannot complete safely."""


def download_raw_dataset(force: bool = False) -> Path:
    """Download the HF CSV into ``data/raw/`` (or reuse a local copy)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_CSV_PATH.exists() and not force:
        logger.info("Using existing raw CSV at %s", RAW_CSV_PATH)
        return RAW_CSV_PATH

    try:
        path = hf_hub_download(
            repo_id=HF_DATASET_ID,
            filename=HF_CSV_FILENAME,
            repo_type="dataset",
            local_dir=str(RAW_DIR),
        )
    except Exception as exc:  # noqa: BLE001 - surface as clear ingest error
        raise IngestError(
            f"Failed to download {HF_DATASET_ID}/{HF_CSV_FILENAME}: {exc}"
        ) from exc

    downloaded = Path(path)
    if downloaded.resolve() != RAW_CSV_PATH.resolve():
        shutil.copy2(downloaded, RAW_CSV_PATH)
    logger.info("Downloaded raw dataset to %s", RAW_CSV_PATH)
    return RAW_CSV_PATH


def load_raw_dataframe(csv_path: Path | None = None) -> pd.DataFrame:
    """Load the raw Zomato CSV and validate required columns."""
    path = csv_path or RAW_CSV_PATH
    if not path.exists():
        raise IngestError(
            f"Raw dataset not found at {path}. Run download/ingest first."
        )

    df = pd.read_csv(path, low_memory=False)
    missing = [c for c in REQUIRED_SOURCE_COLUMNS if c not in df.columns]
    if missing:
        raise IngestError(
            "Dataset schema mismatch: missing required columns "
            f"{missing}. Found columns: {list(df.columns)}"
        )
    return df


def _normalize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    # Collapse internal whitespace
    return re.sub(r"\s+", " ", text)


def parse_rating(value: object) -> float | None:
    """Parse Zomato ``rate`` values like ``4.1/5``, ``NEW``, ``-``."""
    text = _normalize_text(value)
    if text is None:
        return None
    lowered = text.lower().replace(" ", "")
    if lowered in _UNSCORED_RATINGS:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)/5$", lowered)
    if match:
        rating = float(match.group(1))
        return rating if 0.0 <= rating <= 5.0 else None
    try:
        rating = float(lowered)
    except ValueError:
        return None
    return rating if 0.0 <= rating <= 5.0 else None


def parse_cost(value: object) -> float | None:
    """Parse ``approx_cost(for two people)`` (may include commas)."""
    text = _normalize_text(value)
    if text is None:
        return None
    cleaned = text.replace(",", "").replace("₹", "").strip()
    try:
        cost = float(cleaned)
    except ValueError:
        return None
    return cost if cost >= 0 else None


def normalize_location(value: object) -> str | None:
    text = _normalize_text(value)
    if text is None:
        return None
    return text.casefold()


def normalize_cuisine_tokens(value: object) -> list[str]:
    """Split multi-cuisine strings into normalized tokens."""
    text = _normalize_text(value)
    if text is None:
        return []
    tokens: list[str] = []
    seen: set[str] = set()
    for part in text.split(","):
        token = part.strip().casefold()
        token = re.sub(r"\s+", " ", token)
        if token in _NA_CUISINE_TOKENS or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens


def assign_budget_bands(costs: pd.Series) -> tuple[pd.Series, dict[str, float]]:
    """Map costs to low/medium/high using robust tertile cutoffs.

    Rows with missing cost get a null budget band.
    """
    valid = costs.dropna()
    if valid.empty:
        return pd.Series([None] * len(costs), index=costs.index), {
            "low_max": float("nan"),
            "medium_max": float("nan"),
        }

    low_max = float(valid.quantile(1 / 3))
    medium_max = float(valid.quantile(2 / 3))

    def _band(cost: float | None) -> str | None:
        if cost is None or (isinstance(cost, float) and pd.isna(cost)):
            return None
        if cost <= low_max:
            return "low"
        if cost <= medium_max:
            return "medium"
        return "high"

    bands = costs.map(_band)
    return bands, {"low_max": low_max, "medium_max": medium_max}


def transform_restaurants(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean, normalize, dedupe, and band the raw Zomato frame."""
    working = raw.copy()

    working["name"] = working["name"].map(_normalize_text)
    working["location_raw"] = working["location"].map(_normalize_text)
    working["location"] = working["location"].map(normalize_location)
    working["city"] = DEFAULT_CITY.casefold()
    working["city_display"] = DEFAULT_CITY

    if "listed_in(city)" in working.columns:
        working["listed_in_city"] = working["listed_in(city)"].map(_normalize_text)
    else:
        working["listed_in_city"] = None

    working["cuisines_raw"] = working["cuisines"].map(_normalize_text)
    working["cuisine_tokens"] = working["cuisines"].map(normalize_cuisine_tokens)
    working["cuisine_tokens_str"] = working["cuisine_tokens"].map(
        lambda tokens: ", ".join(tokens) if tokens else None
    )

    working["rating"] = working["rate"].map(parse_rating)
    working["cost"] = working["approx_cost(for two people)"].map(parse_cost)
    working["votes"] = pd.to_numeric(working.get("votes"), errors="coerce").fillna(0).astype(int)

    for col, default in (
        ("online_order", None),
        ("book_table", None),
        ("rest_type", None),
        ("address", None),
        ("url", None),
    ):
        if col in working.columns:
            working[col] = working[col].map(_normalize_text)
        else:
            working[col] = default

    # Drop rows without a usable name (D03)
    before = len(working)
    working = working[working["name"].notna()].copy()
    dropped_nameless = before - len(working)

    # Missing location → unknown bucket that won't match normal filters (D04)
    missing_location = working["location"].isna()
    working.loc[missing_location, "location"] = "unknown"
    working.loc[missing_location, "location_raw"] = "Unknown"

    budget_band, cutoffs = assign_budget_bands(working["cost"])
    working["budget_band"] = budget_band

    # Dedupe on name + location; keep highest votes then rating (D08)
    working["_rating_sort"] = working["rating"].fillna(-1.0)
    working = working.sort_values(
        by=["votes", "_rating_sort"], ascending=[False, False]
    )
    before_dedupe = len(working)
    working = working.drop_duplicates(subset=["name", "location"], keep="first")
    dropped_dupes = before_dedupe - len(working)

    processed = working[
        [
            "name",
            "city",
            "city_display",
            "location",
            "location_raw",
            "listed_in_city",
            "cuisines_raw",
            "cuisine_tokens_str",
            "rating",
            "cost",
            "budget_band",
            "votes",
            "online_order",
            "book_table",
            "rest_type",
            "address",
            "url",
        ]
    ].reset_index(drop=True)

    meta = {
        "source_rows": int(len(raw)),
        "processed_rows": int(len(processed)),
        "dropped_nameless": int(dropped_nameless),
        "dropped_duplicates": int(dropped_dupes),
        "budget_cutoffs": cutoffs,
        "cities": sorted(processed["city_display"].dropna().unique().tolist()),
        "locations": int(processed["location"].nunique()),
    }
    return processed, meta


def persist_restaurants(df: pd.DataFrame, destination: Path | None = None) -> Path:
    """Atomically write the processed frame to SQLite (D12)."""
    import sqlite3

    dest = destination or PROCESSED_DB_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Always write .sqlite even if env points at a legacy .parquet path
    if dest.suffix.lower() in {".parquet", ".csv"}:
        dest = dest.with_suffix(".sqlite")

    # Write to a sibling temp file, close the DB handle, then replace.
    # Windows locks open SQLite files, so avoid replacing inside an open context.
    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix="restaurants_",
        suffix=".sqlite",
        dir=str(dest.parent),
    )
    os.close(tmp_fd)
    tmp_path = Path(tmp_name)

    try:
        conn = sqlite3.connect(tmp_path)
        try:
            df.to_sql(RESTAURANTS_TABLE, conn, if_exists="replace", index=False)
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS ix_restaurants_city "
                f"ON {RESTAURANTS_TABLE}(city)"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS ix_restaurants_location "
                f"ON {RESTAURANTS_TABLE}(location)"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS ix_restaurants_budget "
                f"ON {RESTAURANTS_TABLE}(budget_band)"
            )
            conn.commit()
        finally:
            conn.close()

        os.replace(tmp_path, dest)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise

    logger.info("Wrote %s restaurants to %s", len(df), dest)
    return dest


def ingest(
    *,
    force_download: bool = False,
    csv_path: Path | None = None,
    destination: Path | None = None,
) -> dict:
    """Run the full ingest pipeline and return summary metadata."""
    if csv_path is None:
        download_raw_dataset(force=force_download)
        source = RAW_CSV_PATH
    else:
        source = Path(csv_path)

    raw = load_raw_dataframe(source)
    processed, meta = transform_restaurants(raw)
    out_path = persist_restaurants(processed, destination=destination)
    meta["processed_path"] = str(out_path)
    return meta


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    meta = ingest()
    print("Ingest complete:")
    for key, value in meta.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
