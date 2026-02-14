# =====================================================================
# Main Application Entry Point
# =====================================================================
import streamlit as st

# 1. Wide Mode - First Command
st.set_page_config(layout="wide", page_title="Intelligence Matrix", page_icon="\U0001f578\ufe0f")

import pandas as pd
import asyncio
import os
import logging

# Modular Imports
from services.data_loader import load_buyers
from services.search_agent import SearchAgent
from services.database import upsert_company_data

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Title & Header ---
st.title("\U0001f578\ufe0f Intelligence Matrix: Modular Edition")
st.markdown("---")

# --- Load Data ---
@st.cache_data
def get_data():
    raw = load_buyers()
    return pd.DataFrame(raw) if raw else pd.DataFrame()

df = get_data()

if df.empty:
    st.error("No data available. Please check data/combined_buyers.json")
    st.stop()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters")
    
    # Country Filter
    country_col = "destination_country"
    if country_col not in df.columns:
        # Fallback logic
        cols = [c for c in df.columns if "country" in c.lower()]
        country_col = cols[0] if cols else df.columns[1]

    all_countries = sorted(df[country_col].dropna().unique().tolist())
    selected_countries = st.multiselect("Select Country", options=all_countries)
    
    st.info(f"Loaded {len(df)} companies.")

# --- Filter Logic (Strict) ---
if selected_countries:
    dff = df[df[country_col].isin(selected_countries)].copy()
else:
    dff = df.copy()

# --- Search Bar ---
col_search, _ = st.columns([1, 2])
with col_search:
    search_query = st.text_input("Search Company Name", placeholder="Type to filter table...")
    if search_query:
        dff = dff[dff["buyer_name"].str.contains(search_query, case=False, na=False)]

st.markdown(f"**Showing {len(dff)} companies**")

# --- Layout: Table (Left) + Profile (Right) ---
col_table, col_profile = st.columns([0.65, 0.35], gap="large")

with col_table:
    event = st.dataframe(
        dff,
        column_order=["buyer_name", country_col, "total_usd", "email", "phone"],
        column_config={
            "buyer_name": "Company",
            "total_usd": st.column_config.NumberColumn("Volume (USD)", format="$%.2f"),
            "email": "Email",
            "phone": "Phone"
        },
        height=700,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="company_table"
    )

# --- Profile & Scavenge Logic ---
with col_profile:
    selected_rows = event.selection.rows
    
    if selected_rows:
        # Get actual row from filtered dataframe
        # Note: st.dataframe selection indices correspond to the displayed dataframe's numeric index (0, 1, 2...)
        # We need to map it correctly.
        row_idx = selected_rows[0]
        record = dff.iloc[row_idx]
        
        company_name = record["buyer_name"]
        country = record[country_col]
        
        # --- Entity Card ---
        st.markdown(f"""
        <div style="background:#1e1e1e;padding:20px;border-radius:10px;border:1px solid #333;">
            <h2 style="color:#a38cf4;margin:0;">{company_name}</h2>
            <p style="color:#888;font-size:0.9em;text-transform:uppercase;">{country}</p>
            <hr style="border-top:1px solid #333;">
        </div>
        """, unsafe_allow_html=True)
        
        # Check Session State for Enriched Data
        enriched_key = f"enriched_{company_name}"
        scavenged_data = st.session_state.get(enriched_key, {})
        
        # Merge Source + Scavenged Data for Display
        display_email = record.get("email", "")
        if not display_email and scavenged_data.get("emails"):
             display_email = ", ".join(scavenged_data["emails"])
             
        display_phone = record.get("phone", "")
        if not display_phone and scavenged_data.get("phones"):
             display_phone = ", ".join(scavenged_data["phones"])

        # Current Data
        st.write("### \U0001f4ca Contact Info")
        st.text_input("Email", value=str(display_email), disabled=True)
        st.text_input("Phone", value=str(display_phone), disabled=True)
        
        if scavenged_data:
            st.info("Showing enriched data from AI scan.")
        
        st.markdown("---")
        
        # Scavenge Button
        if st.button("\U0001f985 Scavenge Data", type="primary", use_container_width=True):
            agent = SearchAgent()
            
            status = st.status(f"Scavenging for {company_name}...", expanded=True)
            
            async def run_scavenge():
                # 3. Callback wrapper
                def log_status(msg):
                    status.write(msg)
                
                # 4. Search
                return await agent.find_company_leads(company_name, country, callback=log_status)

            # Run Async
            result = asyncio.run(run_scavenge())
            
            status.update(label="Scavenge Complete!", state="complete", expanded=False)
            
            if result and "error" not in result:
                st.success("New Data Found!")
                
                # Save to Session State
                st.session_state[enriched_key] = result
                
                # Auto-Save to Supabase
                with st.spinner("Saving to Leads Database..."):
                    from services.database import save_scavenged_data
                    
                    # Prepare data payload (include country)
                    payload = result.copy()
                    payload["country"] = country
                    
                    db_res = save_scavenged_data(company_name, payload)
                    
                    if db_res and db_res.get("status") == "success":
                        st.success(f"\u2705 New intelligence saved to Supabase for {company_name}")
                    else:
                        st.warning(f"Could not save: {db_res.get('message')}")
                        
                st.rerun()
            else:
                st.error(f"Scavenge Failed: {result.get('message', 'Unknown error')}")
                
    else:
        st.info("Select a company from the list to view profile.")
