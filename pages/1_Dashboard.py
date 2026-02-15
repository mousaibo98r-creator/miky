import streamlit as st

st.title("\U0001f4ca Dashboard")

# --- Heavy imports ONLY inside this page ---
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.database import fetch_all_buyers

random.seed(42)  # Deterministic mock data

# --- Data loads AFTER title renders ---
@st.cache_data(ttl=300)
def get_dashboard_data():
    return fetch_all_buyers()

raw_data = get_dashboard_data()
df = pd.DataFrame(raw_data) if raw_data else None

st.markdown("### Search Exporters")
search_query = st.text_input("Enter Exporter Name, ID, or Region", placeholder="Search...")

col1, col2, col3 = st.columns(3)

if df is not None:
    total_rev_val = df["total_usd"].sum()
    total_rev = f"${total_rev_val / 1000000:.1f}M"
    active_buyers = f"{len(df)}"
    growth = "+12.5%"

    country_counts = df["country_english"].value_counts().head(10).reset_index()
    country_counts.columns = ["Country", "Value"]
    df_b = country_counts

    # Temporal mock (JSON has no dates)
    dates = pd.date_range(start="2023-01-01", periods=12, freq="M")
    df_a = pd.DataFrame(
        {
            "Date": dates,
            "USD Volume": [random.randint(50000, 500000) for _ in range(12)],
            "Count": [random.randint(10, 100) for _ in range(12)],
        }
    )
else:
    st.info("No data file found. Showing demo dashboard.")
    total_rev = "$12.5M"
    active_buyers = "1,240"
    growth = "+15.4%"
    dates = pd.date_range(start="2023-01-01", periods=12, freq="M")
    df_a = pd.DataFrame(
        {
            "Date": dates,
            "USD Volume": [random.randint(50000, 500000) for _ in range(12)],
            "Count": [random.randint(10, 100) for _ in range(12)],
        }
    )
    countries = ["USA", "China", "Germany", "UK", "France", "India"]
    df_b = pd.DataFrame(
        {"Country": countries, "Value": [random.randint(100, 1000) for _ in range(len(countries))]}
    )

with col1:
    st.markdown(
        f'<div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center"><div style="font-size:1rem;color:#fafafa">Total Volume (USD)</div><div style="font-size:2rem;font-weight:bold;color:#00d2ff">{total_rev}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center"><div style="font-size:1rem;color:#fafafa">Active Buyers</div><div style="font-size:2rem;font-weight:bold;color:#00d2ff">{active_buyers}</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
    <div style="background:#262730;padding:20px;border-radius:10px;border:1px solid #41424b;text-align:center">
        <div style="font-size:2rem">\U0001f4c2</div>
        <div style="color:#00d2ff;font-weight:bold">Database</div>
        <div style="color:#999;font-size:0.9rem">Supabase Explorer</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.divider()

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("USD Volume vs Transaction Count")
    fig_a = go.Figure()
    fig_a.add_trace(
        go.Bar(x=df_a["Date"], y=df_a["USD Volume"], name="USD Volume", marker_color="#00d2ff")
    )
    fig_a.add_trace(
        go.Scatter(
            x=df_a["Date"],
            y=df_a["Count"],
            name="Count",
            yaxis="y2",
            line=dict(color="#ff0055", width=3),
        )
    )
    fig_a.update_layout(
        template="plotly_dark",
        yaxis=dict(title="USD Volume"),
        yaxis2=dict(title="Count", overlaying="y", side="right"),
        legend=dict(x=0, y=1.1, orientation="h"),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_a, use_container_width=True)

with c2:
    st.subheader("Top Countries")
    fig_b = px.pie(
        df_b,
        values="Value",
        names="Country",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    fig_b.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_b, use_container_width=True)
