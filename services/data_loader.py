import streamlit as st
import json
import os

# Project root = parent of services/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "combined_buyers.json")


@st.cache_data
def load_buyers():
    """Load buyer data from JSON. Cached after first call. Returns list of dicts."""
    if not os.path.exists(DATA_PATH):
        return None
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Return as list of dicts - pages can convert to DataFrame if needed
        return data
    except Exception:
        return None


def get_buyer_names(data):
    """Return sorted list of buyer names for dropdowns."""
    if not data:
        return []
    names = set()
    for item in data:
        name = item.get('buyer_name', '')
        if name:
            names.add(name)
    return sorted(names)


def get_countries(data):
    """Return sorted list of unique countries."""
    if not data:
        return []
    countries = set()
    for item in data:
        c = item.get('country_english', '')
        if c:
            countries.add(c)
    return sorted(countries)
