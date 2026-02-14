"""Data loader service for buyer JSON data.

Loads, caches, and provides query helpers for the buyer dataset.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import streamlit as st

logger = logging.getLogger(__name__)

# Project root = parent of services/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "combined_buyers.json")


@st.cache_data
def load_buyers() -> Optional[List[Dict[str, Any]]]:
    """Load buyer data from JSON. Cached after first call.

    Returns:
        List of buyer dicts, or None if file is missing/corrupt.
    """
    if not os.path.exists(DATA_PATH):
        logger.warning("Data file not found: %s", DATA_PATH)
        return None
    try:
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Loaded %d buyers from %s", len(data), DATA_PATH)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load buyer data: %s", exc)
        return None


def get_buyer_names(data: Optional[List[Dict[str, Any]]]) -> List[str]:
    """Return sorted list of unique buyer names for dropdowns."""
    if not data:
        return []
    names = {item.get("buyer_name", "") for item in data}
    names.discard("")
    return sorted(names)


def get_countries(data: Optional[List[Dict[str, Any]]]) -> List[str]:
    """Return sorted list of unique countries."""
    if not data:
        return []
    countries = {item.get("country_english", "") for item in data}
    countries.discard("")
    return sorted(countries)
