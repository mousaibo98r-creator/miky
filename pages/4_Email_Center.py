import streamlit as st
import pandas as pd
import asyncio
import os
import logging
import json
from datetime import datetime
from services.search_agent import SearchAgent # Re-use for AI client
from services.database import fetch_all_buyers, get_supabase, bulk_upsert_buyers

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Email Center", page_icon="\U0001f4e7")
st.title("\U0001f4e7 Cold Email Center")
st.markdown("---")

# --- Load Data (Audience) ---
# Fetch all buyers, filter for those with emails
@st.cache_data(ttl=300)
def get_audience():
    raw_data = fetch_all_buyers()
    if not raw_data:
        return pd.DataFrame()
    df = pd.DataFrame(raw_data)
    # Filter: Must have email + email is not empty/none
    def has_email(x):
        return x is not None and str(x).strip().lower() not in ["", "none", "nan", "null"]
    
    if "email" in df.columns:
        df = df[df["email"].apply(has_email)].copy()
        # Convert timestamp for UI
        if "last_contacted_at" in df.columns:
            df["last_contacted_at"] = pd.to_datetime(df["last_contacted_at"], errors="coerce")
        return df
    return pd.DataFrame()

df = get_audience()

if df.empty:
    st.warning("No companies with email addresses found in 'mousa' table.")
    st.stop()

# --- Layout: Audience (Left) | Composer (Right) ---
col_audience, col_composer = st.columns([0.4, 0.6], gap="large")

with col_audience:
    st.subheader("1. Select Audience")
    st.caption(f"Found {len(df)} leads with emails.")
    
    # Selection Table
    # Use dataframe with selection
    # We want multi-select
    
    event = st.dataframe(
        df,
        column_order=["buyer_name", "destination_country", "email", "last_contacted_at"],
        column_config={
            "buyer_name": "Company",
            "last_contacted_at": st.column_config.DatetimeColumn("Last Contact", format="D MMM, YYYY"),
            "email": "Email"
        },
        height=600,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        key="audience_table"
    )
    
    selected_indices = event.selection.rows
    selected_rows = df.iloc[selected_indices] if selected_indices else pd.DataFrame()

with col_composer:
    st.subheader("2. AI Composer")
    
    if selected_rows.empty:
        st.info("Select companies from the left to start drafting.")
    else:
        st.success(f"Selected {len(selected_rows)} companies.")
        
        # Templates
        subject = st.text_input("Subject Line", value="Partnership Opportunity with [My Company]")
        body_template = st.text_area("Body Template (Instructions for AI)", 
                                     value="Write a polite, professional cold email introducing our export services. \nReference their import volume (Total USD) to show we did our research. \nKeep it under 150 words.",
                                     height=150)
        
        # Generate Drafts Button
        if st.button("✨ Generate Personalized Drafts", type="primary"):
            if not os.getenv("DEEPSEEK_API_KEY"):
                st.error("DeepSeek API Key missing.")
            else:
                st.session_state["drafts"] = {} # Clear old drafts
                
                # Progress Bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Re-use SearchAgent for its client (lazy way) or just create new client
                # Let's instantiate SearchAgent just to access the client or copy the client logic?
                # Actually, SearchAgent has the client. Let's use it.
                agent = SearchAgent()
                
                async def generate_draft(company, total_usd, country):
                    prompt = f"""
                    You are an expert sales copywriter.
                    Write a personalized email for:
                    Company: {company}
                    Country: {country}
                    Their Import Volume: ${total_usd:,.2f}
                    
                    Subject: {subject}
                    Instructions: {body_template}
                    
                    Return ONLY the email body text. No subject in body.
                    """
                    
                    try:
                        response = await agent.client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        return f"Error generating draft: {e}"

                # Run Batch Generation
                async def run_batch():
                    tasks = []
                    companies = selected_rows.to_dict("records")
                    
                    for i, row in enumerate(companies):
                        status_text.text(f"Drafting for {row['buyer_name']}...")
                        # rate limit?
                        task = generate_draft(row['buyer_name'], row.get('total_usd', 0), row.get('destination_country', ''))
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks)
                    return results

                drafts = asyncio.run(run_batch())
                
                # Store in Session State
                curr_drafts = {}
                for i, row in enumerate(selected_rows.to_dict("records")):
                    curr_drafts[row['buyer_name']] = drafts[i]
                
                st.session_state["drafts"] = curr_drafts
                status_text.text("Drafting Complete!")
                progress_bar.progress(100)

        # Display Drafts & Send Logic
        if "drafts" in st.session_state and st.session_state["drafts"]:
            st.markdown("### Review Drafts")
            
            # Show drafts in tabs or expander? Expander is cleaner for multiple
            drafts = st.session_state["drafts"]
            
            # Filter drafts to only currently selected (if selection changed)
            # Or just show all generated.
            # Let's show drafts for selected rows.
            
            valid_drafts = {k:v for k,v in drafts.items() if k in selected_rows["buyer_name"].values}
            
            for company, draft in valid_drafts.items():
                with st.expander(f"Draft for {company}", expanded=True):
                    st.text_area("Body", value=draft, height=200, key=f"body_{company}")
            
            st.markdown("---")
            
            # SEND BUTTON
            if st.button("🚀 Send Emails (Simulation)", type="primary"):
                with st.spinner("Sending emails..."):
                    # Update Database 'last_contacted_at'
                    now = datetime.utcnow().isoformat()
                    
                    # Prepare Bulk Upsert
                    updates = []
                    for idx, row in selected_rows.iterrows():
                        updates.append({
                            "buyer_name": row["buyer_name"],
                            "last_contacted_at": now
                        })
                        print(f"Sending email to {row['email']} for {row['buyer_name']}...")
                    
                    # Persist
                    res = bulk_upsert_buyers(updates)
                    
                    if res.get("status") == "success":
                        st.success(f"Successfully sent {len(updates)} emails!")
                        time.sleep(1)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to update database: {res.get('message')}")
