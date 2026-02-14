import streamlit as st
import pandas as pd
import asyncio
import os
import logging

# 1. FORCE WIDE LAYOUT - MUST be the very first Streamlit command
st.set_page_config(layout="wide", page_title="Intelligence Matrix", page_icon="\U0001f578\ufe0f")

# Modular Imports
from services.data_loader import load_buyers
from services.search_agent import SearchAgent
from services.database import save_scavenged_data

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
    
    # Country Filter (Strict Logic)
    country_col = "destination_country"
    
    # Safety Check: Ensure column exists
    if country_col not in df.columns:
        st.error(f"Critical Error: Column '{country_col}' missing from dataset.")
        st.stop()

    # Get unique countries
    all_countries = sorted(df[country_col].dropna().unique().tolist())
    
    # User Selection
    selected_countries = st.multiselect("Select Country", options=all_countries)
    
    st.info(f"Loaded {len(df)} companies.")

# --- Apply Filter (Logic) ---
if selected_countries:
    # Strict filter: Only show rows where destination_country is in selection
    dff = df[df[country_col].isin(selected_countries)].copy()
else:
    dff = df.copy()

# --- Search Bar (Additional Filter) ---
col_search, _ = st.columns([1, 2])
with col_search:
    search_query = st.text_input("Search Company Name", placeholder="Type to filter table...")
    if search_query:
        # Filter by buyer_name
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
        # Map selection index to dataframe index
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
        # If no source email, check scavenged
        if not display_email and scavenged_data.get("emails"):
             display_email = ", ".join(scavenged_data["emails"])
        # If source has list, join it
        elif isinstance(display_email, list):
             display_email = ", ".join(display_email)
             
        display_phone = record.get("phone", "")
        if not display_phone and scavenged_data.get("phones"):
             display_phone = ", ".join(scavenged_data["phones"])
        elif isinstance(display_phone, list):
             display_phone = ", ".join(display_phone)

        # Current Data Display
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
                # Callback wrapper
                def log_status(msg):
                    status.write(msg)
                
                # Search using Agent
                return await agent.find_company_leads(company_name, country, callback=log_status)

            # Run Async
            result = asyncio.run(run_scavenge())
            
            status.update(label="Scavenge Complete!", state="complete", expanded=False)
            
            if result and "error" not in result:
                # 1. Save to Session State (Instant UI Update)
                st.session_state[enriched_key] = result
                
                # 2. Auto-Save to Supabase 'mousa' table
                with st.spinner("Saving logic to Supabase..."):
                    
                    # Prepare payload: pass raw result, database.py handles flattening
                    payload = result.copy()
                    
                    # Save!
                    db_res = save_scavenged_data(company_name, payload)
                    
                    if db_res and db_res.get("status") == "success":
                        st.success(f"\u2705 New intelligence saved to Supabase (mousa) for {company_name}")
                    else:
                        st.warning(f"Could not save: {db_res.get('message')}")
                        
                st.rerun()
            else:
                st.error(f"Scavenge Failed: {result.get('message', 'Unknown error')}")
                
    else:
        st.info("Select a company from the list to view profile.")
