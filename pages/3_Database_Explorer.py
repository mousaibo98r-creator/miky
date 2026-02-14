import streamlit as st
import pandas as pd
from services.database import get_supabase

st.set_page_config(layout="wide", page_title="Database Explorer", page_icon="\U0001f4c2")

st.title("\U0001f4c2 Supabase Data Explorer")

supabase = get_supabase()

if not supabase:
    st.error("Supabase not configured. Check .env")
    st.stop()

# --- Table Selection ---
tables = ["buyers", "leads", "users"] # Common tables
selected_table = st.selectbox("Select Table", tables, index=0)

# --- Fetch Data ---
if st.button("Refresh Data", type="primary"):
    try:
        response = supabase.table(selected_table).select("*").execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            st.success(f"Loaded {len(df)} rows from '{selected_table}'")
            st.dataframe(df, use_container_width=True, height=600)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                csv,
                f"{selected_table}_export.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("Table is empty.")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.warning("Make sure the table exists in Supabase and RLS policies allow read access.")
