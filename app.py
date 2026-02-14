import streamlit as st

# =====================================================================
# PAGE CONFIG — MUST BE THE ABSOLUTE FIRST STREAMLIT COMMAND
# Nothing else (no st.*, no st.secrets, no st.cache) can appear above.
# =====================================================================
st.set_page_config(
    page_title="Export Analytics Platform",
    page_icon="\U0001f30d",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# Standard-library imports only (safe, no side-effects)
# =====================================================================
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root is in Python path (so pages/ can find services/)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =====================================================================
# Load .env file (lightweight, no network I/O, optional dependency)
# =====================================================================
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv is not required on Streamlit Cloud

# =====================================================================
# Bridge st.secrets → os.environ (AFTER set_page_config)
# Streamlit Cloud injects secrets here; we mirror them to os.environ
# so that services/ can read them uniformly via os.environ.
# =====================================================================
try:
    if hasattr(st, "secrets"):
        for key in ("SUPABASE_URL", "SUPABASE_KEY", "DEEPSEEK_API_KEY"):
            if key not in os.environ:
                try:
                    val = st.secrets[key]
                    os.environ[key] = str(val)
                except (KeyError, TypeError):
                    pass
except Exception as exc:
    logger.debug("st.secrets bridge skipped: %s", exc)


# =====================================================================
# HOME PAGE UI — lightweight, no pandas/plotly/supabase at module level
# =====================================================================
st.title("\U0001f30d Export Analytics Platform")

st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; }
    .hero-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #00d2ff33;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-card">
    <h2 style="color: #00d2ff; margin: 0">Welcome to Your Intelligence Hub</h2>
    <p style="color: #ccc; font-size: 1.1rem">
        Navigate using the sidebar to access powerful analytics, buyer intelligence,
        AI-powered data enrichment, and more.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# --- Navigation cards ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f4ca</div>
        <div style="color:#00d2ff;font-weight:bold">Dashboard</div>
        <div style="color:#999;font-size:0.9rem">Charts & KPIs</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f578\ufe0f</div>
        <div style="color:#00d2ff;font-weight:bold">Intelligence</div>
        <div style="color:#999;font-size:0.9rem">Buyer Data Matrix</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f916</div>
        <div style="color:#00d2ff;font-weight:bold">AI Search</div>
        <div style="color:#999;font-size:0.9rem">DeepSeek Enrichment</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.divider()

# --- Environment / system status (env-var check ONLY, no network calls) ---
st.subheader("System Status")
c1, c2, c3 = st.columns(3)

with c1:
    data_file = os.path.join(PROJECT_ROOT, "data", "combined_buyers.json")
    if os.path.exists(data_file):
        size_mb = os.path.getsize(data_file) / (1024 * 1024)
        st.success(f"\u2705 Data file loaded ({size_mb:.1f} MB)")
    else:
        st.warning("\u26a0\ufe0f Data file not found")

with c2:
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        st.success("\u2705 Supabase configured")
    else:
        st.info("\u2139\ufe0f Supabase not configured")

with c3:
    if os.environ.get("DEEPSEEK_API_KEY"):
        st.success("\u2705 DeepSeek AI ready")
    else:
        st.info("\u2139\ufe0f DeepSeek not configured")
