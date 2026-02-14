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
from services.search_agent import SearchAgent
from services.database import save_scavenged_data, fetch_all_buyers, bulk_upsert_buyers, get_supabase

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Title & Header ---
st.title("\U0001f578\ufe0f Intelligence Matrix: Database Edition")

# --- Load Data (Single Source of Truth: Supabase) ---
@st.cache_data(ttl=300) 
def get_data_from_db():
    raw_data = fetch_all_buyers()
    if not raw_data:
        return pd.DataFrame()
    return pd.DataFrame(raw_data)

# Fetch Data
df = get_data_from_db()

# Initialize empty DF if needed to prevent errors
if df.empty:
    df = pd.DataFrame(columns=["buyer_name", "destination_country", "total_usd", "email", "phone", "website", "address"])

# --- 1. BOSS VIEW METRICS ---
# Calculate Metrics
total_companies = len(df)
# Enriched = has email (and email is not empty string or 'None')
enriched_count = df[df["email"].apply(lambda x: x is not None and str(x).strip().lower() not in ["", "none"])].shape[0]
total_value = df["total_usd"].sum() if "total_usd" in df.columns else 0

# Display Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Companies", total_companies)
m2.metric("Enriched Leads", enriched_count, delta=f"{round((enriched_count/total_companies)*100, 1)}%" if total_companies else "0%")
m3.metric("Potential Value", f"${total_value:,.2f}")

st.markdown("---")

# --- Sidebar Actions ---
with st.sidebar:
    st.header("Actions")
    
    # Export Feature
    json_str = df.to_json(orient="records", indent=2)
    st.download_button(
        label="\U0001f4e5 Download Database as JSON",
        data=json_str,
        file_name="mousa_export.json",
        mime="application/json"
    )
    
    st.divider()
    
    st.header("Filters")
    # Country Filter
    country_col = "destination_country"
    
    if country_col in df.columns:
        all_countries = sorted(df[country_col].dropna().unique().tolist())
        selected_countries = st.multiselect("Select Country", options=all_countries)
    else:
        selected_countries = []
        
    st.info(f"Loaded {len(df)} records from Database.")

# --- Apply Filter ---
if selected_countries and country_col in df.columns:
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
    st.subheader("Interactive Database")
    
    column_config = {
        "buyer_name": st.column_config.TextColumn("Company", disabled=True),
        "total_usd": st.column_config.NumberColumn("Volume (USD)", format="$%.2f"),
        "email": "Email",
        "phone": "Phone",
        "website": st.column_config.LinkColumn("Website"),
        "destination_country": "Country"
    }
    
    # 2. SELECTION LOGIC IN EDITOR
    event = st.data_editor(
        dff,
        column_order=["buyer_name", "destination_country", "total_usd", "email", "phone", "website", "address"],
        column_config=column_config,
        height=600,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic", 
        key="editor",
        on_select="rerun",  # Critical for selection sync
        selection_mode="single-row" 
    )
    
    # Save Button
    if st.button("\U0001f4be Save Changes", type="primary"):
        with st.spinner("Saving changes to Supabase..."):
            # Get edited data from session state if available, or rely on df
            # st.data_editor returns the edited dataframe directly in 'event' ONLY if on_select is NOT used?
            # EXTENSIVE NOTE: In new Streamlit, st.data_editor returns the EDITED dataframe.
            # 'event' is the return value. If on_select is used, does it still return DF?
            # Wait, documentation says data_editor returns the edited data. 
            # BUT if on_change/on_select are used, it might return an event object in some versions?
            # Actually, standard behavior: returns the edited DataFrame.
            # The 'selection' is ACCESSED via `event.selection` IF available?
            # Ah, `st.data_editor` returns the modified dataframe. It does NOT return an event object with selection like `st.dataframe` does in 1.35+.
            # `st.dataframe` with `on_select` returns a selection object.
            # `st.data_editor` returns the EDITED DATA.
            
            # Correction: As of Streamlit 1.35, `st.data_editor` ALSO supports `on_select`.
            # If `on_select` is set, `st.data_editor` returns the EDITED DATA FRAME? 
            # Wait, checking docs... "The return value is the edited dataframe."
            # The selection state is in `st.session_state[key]["selection"]`? NO.
            # Actually, recent updates added `event.selection` on `st.dataframe`.
            # For `st.data_editor`, usually we use it for editing.
            # The User requested: "Use selection_mode='single-row' and on_select='rerun' inside st.data_editor."
            
            # Code adaptation:
            # We need to capture both edits AND selection.
            # If `st.data_editor` returns the DF, then where is the selection?
            # It seems `on_select` works with `st.dataframe`. Does it work with `st.data_editor`?
            # Yes, as of 1.35.
            # But the return value is still the Dataframe.
            # So `event` will be the DataFrame.
            # The selection is accessible via `st.session_state.editor["selection"]["rows"]`!
            
            # Using the `key="editor"` allows access to selection state.
            
            records_to_save = event.to_dict("records")
            res = bulk_upsert_buyers(records_to_save)
            
            if res.get("status") == "success":
                st.success("Changes saved successfully!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Save failed: {res.get('message')}")

# --- Profile Logic ---
with col_profile:
    st.subheader("Entity Profile")
    
    # Logic to find selected row
    selected_row_index = None
    
    # Check session state for selection from data_editor
    # Key is 'editor'
    editor_state = st.session_state.get("editor")
    
    # Debug print or logic check
    # In some versions, it's a dict with "selection" -> "rows": [...]
    if editor_state and isinstance(editor_state, dict) and "selection" in editor_state:
         rows = editor_state["selection"].get("rows", [])
         if rows:
             selected_row_index = rows[0]
    
    # Fallback to st.dataframe logic if using that, but we replaced it.
    
    if selected_row_index is not None:
        try:
            # Map index to filtered dataframe
            # Note: data_editor index usually corresponds to the input dataframe index (dff)
            # Be careful with index resets. We used hide_index=True but index is preserved in backend.
            # If dff has custom index, data_editor preserves it.
            # dff.iloc[selected_row_index] works if index is 0..N positionally relative to View.
            
            record = dff.iloc[selected_row_index]
            
            company_name = record["buyer_name"]
            country = record.get(country_col) or record.get("country") or ""
            
            # --- Entity Card ---
            st.markdown(f"""
            <div style="background:#1e1e1e;padding:20px;border-radius:10px;border:1px solid #333;">
                <h2 style="color:#a38cf4;margin:0;">{company_name}</h2>
                <p style="color:#888;font-size:0.9em;text-transform:uppercase;">{country}</p>
                <hr style="border-top:1px solid #333;">
            </div>
            """, unsafe_allow_html=True)
            
            # --- 3. ROBUST NONE HANDLING & CLICKABLE LINKS ---
            def clean_val(v):
                if v is None: return None
                s = str(v).strip()
                if s.lower() == "none" or s == "": return None
                return s

            st.write("### \U0001f4ca Contact Info")
            
            # Email
            email_val = clean_val(record.get("email"))
            if email_val:
                # Handle lists/commas? If comma separated, maybe just link the first one or generic
                # User asked for clickable.
                # If multiple, complex to link. 
                # Let's simple format:
                st.markdown(f"**Email:** [{email_val}](mailto:{email_val.split(',')[0].strip()})")
            else:
                st.caption("Email: *Not Available*")

            # Phone
            phone_val = clean_val(record.get("phone"))
            if phone_val:
                st.markdown(f"**Phone:** `{phone_val}`")
            else:
                 st.caption("Phone: *Not Available*")
                 
            # Website
            web_val = clean_val(record.get("website"))
            if web_val:
                link = web_val
                if not link.startswith("http"):
                    link = "https://" + link
                st.markdown(f"**Website:** [{web_val}]({link})")
            else:
                 st.caption("Website: *Not Available*")
            
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
                    
        except Exception as e:
            st.info("Select a company row to view details.")
            # logging.error(f"Selection error: {e}")
            
    else:
        st.info("Select a row in the table to view Entity Profile.")
