import streamlit as st
import pandas as pd
import asyncio
import os
import logging
import time
import json

# 1. FORCE WIDE LAYOUT - MUST be the very first Streamlit command
st.set_page_config(layout="wide", page_title="Intelligence Matrix", page_icon="\U0001f578\ufe0f")

# Modular Imports
# Note: services.data_loader is no longer used for local JSON
from services.search_agent import SearchAgent
from services.database import save_scavenged_data, fetch_all_buyers, bulk_upsert_buyers

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Title & Header ---
st.title("\U0001f578\ufe0f Intelligence Matrix: Database Edition")
st.markdown("---")

# --- Load Data (Single Source of Truth: Supabase) ---
@st.cache_data(ttl=300) # Cache to prevent spamming DB on every rerun
def get_data_from_db():
    raw_data = fetch_all_buyers()
    if not raw_data:
        return pd.DataFrame()
    return pd.DataFrame(raw_data)

# Fetch Data
df = get_data_from_db()

# Handle Empty State
if df.empty:
    st.warning("No data found in Supabase 'mousa' table.")
    # Initialize empty DF with expected columns to avoid errors
    df = pd.DataFrame(columns=["buyer_name", "destination_country", "total_usd", "email", "phone", "website", "address"])

# --- Sidebar Actions ---
with st.sidebar:
    st.header("Actions")
    
    # 3. Export Feature
    json_str = df.to_json(orient="records", indent=2)
    st.download_button(
        label="\U0001f4e5 Download Database as JSON",
        data=json_str,
        file_name="mousa_export.json",
        mime="application/json"
    )
    
    st.divider()
    
    st.header("Filters")
    # Country Filter (Strict Logic)
    country_col = "destination_country"
    
    # Ensure column exists (Supabase might return different case/columns?)
    # Normalize if needed, but assuming user Schema is consistent
    if country_col not in df.columns:
         # Fallback or warn?
         # If data comes from CSV import, keys should look like CSV headers or JSON keys
         # If DB columns are different, we might need mapping. 
         # Assuming DB columns match JSON keys exactly based on previous refactors.
         pass 

    if country_col in df.columns:
        all_countries = sorted(df[country_col].dropna().unique().tolist())
        selected_countries = st.multiselect("Select Country", options=all_countries)
    else:
        selected_countries = []
        
    st.info(f"Loaded {len(df)} records from Database.")

# --- Apply Filter (Logic) ---
if selected_countries and country_col in df.columns:
    dff = df[df[country_col].isin(selected_countries)].copy()
else:
    dff = df.copy()

# --- Search Bar ---
col_search, _ = st.columns([1, 2])
with col_search:
    search_query = st.text_input("Search Company Name", placeholder="Type to filter table...")
    if search_query:
         # Case insensitive search
         dff = dff[dff["buyer_name"].str.contains(search_query, case=False, na=False)]

st.markdown(f"**Showing {len(dff)} companies**")

# --- Layout: Table (Left) + Profile (Right) ---
col_table, col_profile = st.columns([0.65, 0.35], gap="large")

with col_table:
    # 2. Manual Editing & Saving
    st.subheader("Interactive Database")
    
    # Configuration for columns
    column_config = {
        "buyer_name": st.column_config.TextColumn("Company", disabled=True), # PK should not be editable here easily
        "total_usd": st.column_config.NumberColumn("Volume (USD)", format="$%.2f"),
        "email": "Email",
        "phone": "Phone",
        "website": st.column_config.LinkColumn("Website"),
        "destination_country": "Country"
    }
    
    # Editable Dataframe
    edited_df = st.data_editor(
        dff,
        column_order=["buyer_name", "destination_country", "total_usd", "email", "phone", "website", "address"],
        column_config=column_config,
        height=600,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic", # Allow add/delete
        key="editor" 
    )
    
    # Save Button
    if st.button("\U0001f4be Save Changes", type="primary"):
        with st.spinner("Saving changes to Supabase..."):
            # Convert edited DF to dict records
            records_to_save = edited_df.to_dict("records")
            
            # This blindly upserts EVERYTHING in the view. 
            # For massive datasets, we should only upsert changes, strictly speaking.
            # But st.data_editor state usage is complex. 
            # Given user request "take the edited data... and upsert", this is the direct implementation.
            
            res = bulk_upsert_buyers(records_to_save)
            
            if res.get("status") == "success":
                st.success("Changes saved successfully!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Save failed: {res.get('message')}")

# --- Profile & Scavenge Logic ---
with col_profile:
    # How to get selection from data_editor?
    # st.data_editor doesn't support 'on_select' event returning row index as cleanly as st.dataframe in older versions,
    # BUT in recent Streamlit (1.35+), `on_select` is available or selection state.
    # However, standard data_editor is primarily for editing.
    # To keep Profile functionality, we might need a separate selection mechanism or rely on `on_select` if available.
    # Let's try to use the `selection` parameter if supported, or fallback to a selectbox if not.
    
    # Actually, st.data_editor DOES support `on_select` in latest versions.
    # Let's assume user has a compatible version (since requirements.txt has streamlit).
    # If not, we might need a workaround. But let's try the modern way first.
    
    # If on_select is NOT supported for data_editor in the installed version, 
    # we might need to rely on the user clicking a row? 
    # Current Streamlit stable `data_editor` does NOT always support row selection events for external usages like `dataframe`.
    # Workaround: Add a "Select" checkbox column? Or just a Selectbox for the 'Profile' view.
    
    st.subheader("Company Profile")
    
    # Dropdown to select company from the CURRENT filtered view
    company_options = dff["buyer_name"].tolist()
    
    if company_options:
        selected_company = st.selectbox("Select Company to Profile", options=company_options)
        
        # Get record
        record = dff[dff["buyer_name"] == selected_company].iloc[0]
        
        company_name = record["buyer_name"]
        # .get with default safely
        country = record.get(country_col) or record.get("country") or ""
        
        # --- Entity Card ---
        st.markdown(f"""
        <div style="background:#1e1e1e;padding:20px;border-radius:10px;border:1px solid #333;">
            <h2 style="color:#a38cf4;margin:0;">{company_name}</h2>
            <p style="color:#888;font-size:0.9em;text-transform:uppercase;">{country}</p>
            <hr style="border-top:1px solid #333;">
        </div>
        """, unsafe_allow_html=True)
        
        # Display Current Info
        st.write("### \U0001f4ca Contact Info")
        st.text_input("Email", value=str(record.get("email", "")), disabled=True)
        st.text_input("Phone", value=str(record.get("phone", "")), disabled=True)
        st.text_input("Website", value=str(record.get("website", "")), disabled=True)

        st.markdown("---")
        
        # Scavenge Button
        if st.button("\U0001f985 Scavenge Data", type="primary", use_container_width=True, key=f"scavenge_{company_name}"):
            agent = SearchAgent()
            
            status = st.status("Scavenging intelligence from the web...", expanded=True)
            
            async def run_scavenge():
                def log_status(msg):
                    status.write(msg)
                return await agent.find_company_leads(company_name, country, callback=log_status)

            result = asyncio.run(run_scavenge())
            
            status.update(label="Scavenge Complete!", state="complete", expanded=False)
            
            if result and "error" not in result:
                # Save to DB (Auto-Save)
                with st.spinner("Saving logic to Supabase..."):
                    payload = result.copy()
                    db_res = save_scavenged_data(company_name, payload)
                    
                    if db_res and db_res.get("status") == "success":
                        st.success(f"Saved to Supabase!")
                        st.toast('Data saved! Refreshing view...', icon='🔄')
                        time.sleep(1.5)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning(f"Could not save: {db_res.get('message')}")
            else:
                st.error(f"Scavenge Failed: {result.get('message')}")

    else:
        st.info("No companies match filter.")
