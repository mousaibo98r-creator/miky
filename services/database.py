import streamlit as st
import os


def _get_secret(key):
    """Get secret from env vars first, then st.secrets as fallback."""
    val = os.environ.get(key, '')
    if val:
        return val
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return ''


@st.cache_resource
def get_supabase_client():
    """Create Supabase client once from env vars. Returns None if unavailable."""
    try:
        from supabase import create_client
    except ImportError:
        return None

    url = _get_secret('SUPABASE_URL')
    key = _get_secret('SUPABASE_KEY')
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None
