import streamlit as st
import pandas as pd
import json
import os

# Project root = parent of services/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "combined_buyers.json")


@st.cache_data
def load_buyers():
    """Load buyer data from JSON. Cached after first call."""
    if not os.path.exists(DATA_PATH):
        return None
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        return None


def get_buyer_names(df):
    """Return sorted list of buyer names for dropdowns."""
    if df is None or df.empty:
        return []
    return sorted(df['buyer_name'].dropna().unique().tolist())


def get_countries(df):
    """Return sorted list of unique countries."""
    if df is None or df.empty:
        return []
    return sorted(df['country_english'].dropna().unique().tolist())
