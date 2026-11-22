"""Paths and dataset constants for the restaurant store."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

HF_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
HF_CSV_FILENAME = "zomato.csv"
RAW_CSV_PATH = RAW_DIR / HF_CSV_FILENAME

DEFAULT_PROCESSED_DB = PROCESSED_DIR / "restaurants.sqlite"
PROCESSED_DB_PATH = Path(
    os.getenv("PROCESSED_DATA_PATH", str(DEFAULT_PROCESSED_DB))
)
if not PROCESSED_DB_PATH.is_absolute():
    PROCESSED_DB_PATH = PROJECT_ROOT / PROCESSED_DB_PATH

RESTAURANTS_TABLE = "restaurants"

# Required source columns from the Zomato CSV
REQUIRED_SOURCE_COLUMNS = (
    "name",
    "location",
    "cuisines",
    "approx_cost(for two people)",
    "rate",
)
