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
total_companies = len(df)
enriched_count = df[df["email"].apply(lambda x: x is not None and str(x).strip().lower() not in ["", "none", "nan"])].shape[0]
total_value = df["total_usd"].sum() if "total_usd" in df.columns else 0

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
            # Get latest data from editor (returned by st.data_editor)
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
    
    # Check session state for selection keys
    if "editor" in st.session_state:
        selection = st.session_state["editor"].get("selection", {})
        rows = selection.get("rows", [])
        if rows:
            selected_row_index = rows[0]
            
    if selected_row_index is not None:
        try:
            # Map index to filtered dataframe
            # Be mindful of index filtering. reset_index() might be needed for mapping if indices are non-sequential?
            # data_editor operates on the passed dataframe index.
            # dff.iloc works positionally. BUT the selection index from data_editor is based on the DISPLAYED index (0 to N).
            # So dff.iloc[selected_row_index] is correct IF dff is the exact input.
            
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
            
            # --- 3. ROBUST HIDDEN FIELDS ---
            def is_valid(v):
                if v is None: return False
                s = str(v).strip()
                return s.lower() not in ["none", "nan", "null", ""]

            st.write("### \U0001f4ca Contact Info")
            
            has_info = False
            
            # Email
            email_val = record.get("email")
            if is_valid(email_val):
                has_info = True
                clean_email = str(email_val).strip()
                first_email = clean_email.split(',')[0].strip()
                st.markdown(f"**Email:** [{clean_email}](mailto:{first_email})")

            # Phone
            phone_val = record.get("phone")
            if is_valid(phone_val):
                has_info = True
                st.markdown(f"**Phone:** `{str(phone_val).strip()}`")
                 
            # Website
            web_val = record.get("website")
            if is_valid(web_val):
                has_info = True
                clean_web = str(web_val).strip()
                link = clean_web
                if not link.startswith("http"):
                    link = "https://" + link
                st.markdown(f"**Website:** [{clean_web}]({link})")
            
            if not has_info:
                st.info("No contact information available.")
            
            st.markdown("---")
            
            # Scavenge Button
            if st.button("\U0001f50d Scavenge Data", type="primary", use_container_width=True, key=f"scavenge_{company_name}"):
                agent = SearchAgent()
                status_container = st.status("🔍 Scavenging intelligence from the web...", expanded=True)
                
                async def run_scavenge():
                    def log_status(msg):
                        status_container.write(msg)
                    return await agent.find_company_leads(company_name, country, callback=log_status)

                try:
                    # Run the search
                    result = asyncio.run(run_scavenge())
                    
                    # Check if we got valid data
                    if result and result.get("status") != "error":
                        status_container.update(label="✅ Scavenge Complete!", state="complete", expanded=False)
                        
                        # Show what we found
                        found_items = []
                        if result.get("emails"):
                            found_items.append(f"{len(result['emails'])} email(s)")
                        if result.get("phones"):
                            found_items.append(f"{len(result['phones'])} phone(s)")
                        if result.get("website"):
                            found_items.append("website")
                        if result.get("address"):
                            found_items.append("address")
                        
                        if found_items:
                            st.info(f"📊 Found: {', '.join(found_items)}")
                        else:
                            st.warning("⚠️ No contact information found for this company")
                        
                        # Save to Supabase
                        with st.spinner("💾 Saving to database..."):
                            db_res = save_scavenged_data(company_name, result)
                            
                            if db_res and db_res.get("status") == "success":
                                st.success(f"✅ {db_res.get('message', 'Saved successfully!')}")
                                st.toast('🔄 Data saved! Refreshing...', icon='✅')
                                time.sleep(1)
                                
                                # Clear cache and refresh
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"❌ Save failed: {db_res.get('message')}")
                    else:
                        status_container.update(label="❌ Search Failed", state="error", expanded=True)
                        error_msg = result.get('message', 'Unknown error occurred')
                        st.error(f"❌ {error_msg}")
                        
                        # Show helpful suggestions
                        with st.expander("💡 Troubleshooting Tips"):
                            st.markdown("""
                            **Possible reasons:**
                            1. Company name might be spelled differently online
                            2. Company might be a smaller/newer business without web presence
                            3. Company might operate under a different legal name
                            4. Search API rate limits (wait a moment and try again)
                            
                            **What to try:**
                            - Check if the company name is exact
                            - Try searching manually on Google first
                            - Look for alternative company names
                            - Try again in a few seconds
                            """)
                        
                except Exception as e:
                    status_container.update(label="❌ Error Occurred", state="error", expanded=True)
                    st.error(f"❌ Unexpected error: {str(e)}")
                    logging.error(f"Scavenge error for {company_name}: {e}")
                    
        except Exception as e:
            st.info("Select a company row to view details.")
            
    else:
        st.info("Select a row in the table to view Entity Profile.")
