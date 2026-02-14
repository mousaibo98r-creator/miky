import streamlit as st
import os

@st.cache_resource
def get_supabase_client():
    """Create Supabase client once from env vars. Returns None if unavailable."""
    try:
        from supabase import create_client
    except ImportError:
        return None

    url = os.environ.get('SUPABASE_URL', '') or st.secrets.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '') or st.secrets.get('SUPABASE_KEY', '')
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None
