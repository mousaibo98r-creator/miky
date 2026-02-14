import streamlit as st
import os

# Load environment variables (lightweight, no network I/O)
from dotenv import load_dotenv
load_dotenv()

# =====================================================================
# PAGE CONFIG - FIRST STREAMLIT COMMAND
# =====================================================================
st.set_page_config(
    page_title="Export Analytics Platform",
    page_icon="\U0001f30d",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# LIGHTWEIGHT HOME PAGE - NO pandas, plotly, supabase, or AI imports
# =====================================================================
st.title("\U0001f30d Export Analytics Platform")

st.markdown("""
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
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <h2 style="color: #00d2ff; margin: 0">Welcome to Your Intelligence Hub</h2>
    <p style="color: #ccc; font-size: 1.1rem">
        Navigate using the sidebar to access powerful analytics, buyer intelligence,
        AI-powered data enrichment, and more.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Quick stats (no data loading, just navigation cards) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f4ca</div>
        <div style="color:#00d2ff;font-weight:bold">Dashboard</div>
        <div style="color:#999;font-size:0.9rem">Charts & KPIs</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f578\ufe0f</div>
        <div style="color:#00d2ff;font-weight:bold">Intelligence</div>
        <div style="color:#999;font-size:0.9rem">Buyer Data Matrix</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f916</div>
        <div style="color:#00d2ff;font-weight:bold">AI Search</div>
        <div style="color:#999;font-size:0.9rem">DeepSeek Enrichment</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Environment status (no network calls) ---
st.subheader("System Status")
c1, c2, c3 = st.columns(3)

with c1:
    data_file = os.path.join(os.path.dirname(__file__), "data", "combined_buyers.json")
    if os.path.exists(data_file):
        size_mb = os.path.getsize(data_file) / (1024 * 1024)
        st.success(f"\u2705 Data file loaded ({size_mb:.1f}MB)")
    else:
        st.warning("\u26a0\ufe0f Data file not found")

with c2:
    if os.environ.get('SUPABASE_URL'):
        st.success("\u2705 Supabase configured")
    else:
        st.info("\u2139\ufe0f Supabase not configured")

with c3:
    if os.environ.get('DEEPSEEK_API_KEY'):
        st.success("\u2705 DeepSeek AI ready")
    else:
        st.info("\u2139\ufe0f DeepSeek not configured")
