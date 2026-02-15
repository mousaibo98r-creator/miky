import streamlit as st

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(layout="wide", page_title="Intelligence Matrix")

import asyncio
import json
import os
import textwrap
import re

import pandas as pd

from services.data_loader import load_buyers
from services.deepseek_client import DeepSeekClient

st.title("\U0001f578\ufe0f Intelligence Matrix")

# --- Heavy imports ONLY inside this page ---
# (none currently needed beyond top-level)

# --- Data loads AFTER title renders ---
raw_data = load_buyers()
df = pd.DataFrame(raw_data) if raw_data else None

if df is not None and not df.empty:
    df_intel = df.copy()
else:
    # Mock fallback
    import random

    names = ["TechGlobal Inc", "Oceanic Trade", "FastLogistics", "Alpha Foods", "Zenith Parts"]
    countries = ["USA", "Germany", "China", "UK", "UAE", "Turkey"]
    mock_data = []
    for i in range(50):
        mock_data.append(
            {
                "buyer_name": random.choice(names),
                "destination_country": random.choice(countries),
                "company_name_english": random.choice(names),
                "country_english": random.choice(countries),
                "country_code": "+1",
                "total_invoices": random.randint(1, 50),
                "total_usd": random.randint(1000, 100000),
                "email": [f"contact{i}@example.com"],
                "exporters": {"Mock Exporter": 1},
                "phone": [f"+1-555-01{i:02d}"],
                "address": [f"{random.randint(100, 999)} Business Rd"],
                "website": ["http://example.com"],
            }
        )
    df_intel = pd.DataFrame(mock_data)
    if not raw_data:
        st.info("No data file found. Showing demo data.")

# --- Filters in Sidebar ---
with st.sidebar:
    st.markdown("### \U0001f50d Filters")
    # Determine country column
    country_col = "destination_country"
    if country_col not in df_intel.columns:
        if "country_english" in df_intel.columns:
            country_col = "country_english"
        else:
            country_col = df_intel.columns[1] # fallback to 2nd col

    # Get unique countries
    countries = sorted(list(df_intel[country_col].dropna().unique()))
    sel_country = st.multiselect("Country", options=countries)

    st.divider()

    # --- EXPLICIT FILTER LOGIC ---
    if sel_country:
        # User selected countries -> Filter rows
        dff = df_intel[df_intel[country_col].isin(sel_country)].copy()
    else:
        # No selection -> Show all
        dff = df_intel.copy()

# --- Main Layout: Side-by-Side [Matrix 70% | Profile 30%] ---
col_matrix, col_profile = st.columns([2.8, 1.2])

with col_matrix:
    # Search Bar (Full width of table area)
    txt_search = st.text_input("Search Buyers", placeholder="Type to filter...")
    if txt_search:
        dff = dff[dff["buyer_name"].str.contains(txt_search, case=False, na=False)]

    st.info(f"Showing {len(dff)} records")

    # Data Matrix
    if not dff.empty:
        # Pre-process list columns
        dff_display = dff.copy()
        
        def safe_join(x, sep=", "):
            if isinstance(x, list):
                return sep.join([str(i) for i in x if i])
            return str(x) if pd.notna(x) else ""

        dff_display["emails_display"] = dff_display["email"].apply(lambda x: safe_join(x))
        dff_display["phones_display"] = dff_display["phone"].apply(lambda x: safe_join(x))
        dff_display["websites_display"] = dff_display["website"].apply(lambda x: safe_join(x))
        dff_display["addresses_display"] = dff_display["address"].apply(lambda x: safe_join(x, "; "))
        
        # Ensure total_invoices exists
        if "total_invoices" not in dff_display.columns:
            dff_display["total_invoices"] = 0

        # Column Order
        display_cols = [
            "buyer_name",
            country_col,
            "total_usd",
            "emails_display",
            "total_invoices",
            "phones_display",
            "websites_display",
            "addresses_display",
        ]

        # Use dff_display for the table
        event = st.dataframe(
            dff_display[display_cols],
            column_config={
                "buyer_name": "Buyer Name",
                country_col: "Country",
                "total_usd": st.column_config.NumberColumn("Total USD", format="$%.2f"),
                "emails_display": "Email",
                "total_invoices": st.column_config.NumberColumn("Invoices"),
                "phones_display": "Phone",
                "websites_display": "Website",
                "addresses_display": "Address",
            },
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            height=600,
        )
    else:
        event = None
        st.warning("No records found.")

with col_profile:
    st.markdown("### Entity Profile")

    # --- CSS for Obsidian Vertical Card ---
    st.markdown(
        """
        <style>
            .obsidian-card {
                background-color: #111;
                border: 1px solid #333;
                border_radius: 8px;
                padding: 24px;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            .obs-header {
                font-size: 1.4rem;
                font-weight: 700;
                color: #a38cf4;
                margin-bottom: 4px;
                line-height: 1.2;
                word-wrap: break-word;
            }
            .obs-sub {
                font-size: 0.75rem;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 24px;
                word-wrap: break-word;
            }
            .obs-section-label {
                font-size: 0.7rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
                margin-bottom: 4px;
            }
            .obs-value {
                font-size: 1.0rem;
                font-weight: 600;
                color: #fff;
            }
            .obs-grid-2 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 24px;
                border-bottom: 1px solid #222;
                padding-bottom: 16px;
            }
            .obs-list-section {
                margin-bottom: 16px;
            }
            .obs-list-title {
                color: #a38cf4;
                font-size: 0.75rem;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            .obs-scavenge-tag {
                display: inline-block;
                background-color: #222;
                color: #666;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.7rem;
                margin-top: 10px;
            }
            .obs-placeholder {
                color: #444;
                font-style: italic;
                font-size: 0.85rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if event and event.selection.rows:
        # Get the selected row index from the VIEW (dff), but match it to the filtered dataframe
        # event.selection.rows is a list of row INDICES of the displayed table
        # Since we reset index? No, hide_index=True does not reset index in data
        # BUT default st.dataframe index is 0,1,2... of the displayed data.
        # So we must use iloc on dff, NOT df_intel
        idx = event.selection.rows[0]
        record = dff.iloc[idx] # Use dff (filtered)

        # --- Data Prep ---
        buyer_raw = record.get("buyer_name", "")
        english_name = record.get("company_name_english", "") or buyer_raw

        dest_country = record.get("destination_country", "N/A")
        try:
            dest_country = dest_country.replace("İ", "I").replace("Ç", "C").replace("Ş", "S")
        except AttributeError:
            pass
        country_code = record.get("country_code", "")
        location_str = f"{dest_country} ({country_code})" if country_code else dest_country

        volume = record.get("total_usd", 0)
        
        def to_list(val):
            if isinstance(val, list): return val
            if pd.isna(val) or val == "": return []
            return [str(val)]

        emails = to_list(record.get("email", []))
        websites = to_list(record.get("website", []))
        phones = to_list(record.get("phone", []))
        addresses = to_list(record.get("address", []))

        # Check for SCAVENGED data in session state for this buyer
        scavenge_key = f"scavenged_{buyer_raw}"
        is_scavenged = False
        if scavenge_key in st.session_state:
            scav_data = st.session_state[scavenge_key]
            
            # Simple merge logic for UI display
            if scav_data.get("emails"):
                emails = list(set(emails + scav_data["emails"]))
            if scav_data.get("phones"):
                phones = list(set(phones + scav_data["phones"]))
            if scav_data.get("website"):
                w = scav_data["website"]
                if isinstance(w, list): websites = list(set(websites + w))
                elif isinstance(w, str) and w: websites = list(set(websites + [w]))
            if scav_data.get("address"):
                a = scav_data["address"]
                if isinstance(a, list): addresses = list(set(addresses + a))
                elif isinstance(a, str) and a: addresses = list(set(addresses + [a]))
            is_scavenged = True

        def render_list_items(items, color="#00ffcc"):
            if not items:
                return "<div style='color:#555;font-style:italic;font-size:0.85rem'>None</div>"
            html = ""
            for it in items:
                html += f"<div style='margin-bottom:4px;color:#eee;font-size:0.85rem;word-break:break-all'><span style='color:{color};margin-right:8px'>●</span>{it}</div>"
            return html

        # --- Vertical Obsidian Card ---
        card_content = textwrap.dedent(f"""
            <!-- Header -->
            <div class="obs-header">{buyer_raw}</div>
            <div class="obs-sub">ENGLISH: {english_name}</div>

            <!-- Metrics -->
            <div class="obs-grid-2">
                <div>
                    <div class="obs-section-label">LOCATION</div>
                    <div class="obs-value">{location_str}</div>
                </div>
                <div>
                    <div class="obs-section-label">VOLUME</div>
                    <div class="obs-value">${volume:,.2f}</div>
                </div>
            </div>

            <!-- Lists -->
            <div class="obs-list-section">
                <div class="obs-list-title">EMAILS</div>
                {render_list_items(emails, "#00d2ff")}
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title">WEBSITES</div>
                {render_list_items(websites, "#00d2ff")}
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title">PHONES (WhatsApp)</div>
                {render_list_items(phones, "#a38cf4")}
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title">ADDRESSES</div>
                {render_list_items(addresses, "#ccc")}
            </div>

            {f'<div class="obs-scavenge-tag">NEW DATA FOUND</div>' if is_scavenged else ''}
        """)

        st.markdown(f'<div class="obsidian-card">{card_content}</div>', unsafe_allow_html=True)

        st.markdown("")  # spacer

        # Actions
        st.link_button(
            "\U0001f30d Google Search",
            f"https://www.google.com/search?q={english_name}",
            use_container_width=True,
        )

        if st.button("\U0001f985 Scavenge Data", use_container_width=True):
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                st.error("Please set DEEPSEEK_API_KEY in .env")
            else:
                status_box = st.empty()
                status_box.info("Initializing Agent...")
                
                def update_status(msg):
                    status_box.info(f"\U0001f916 Agent: {msg}")

                with st.spinner("Scavenging deep web..."):
                    try:
                        client = DeepSeekClient(api_key=api_key)

                        async def run_scavenge():
                            return await client.extract_company_data(
                                system_prompt="You are a research agent. Use 'web_search' to find the company website. Use 'fetch_page' to read it. Return valid JSON keys: emails, phones, website, address.",
                                buyer_name=buyer_raw,
                                country=dest_country,
                                callback=update_status
                            )

                        result_json, turns = asyncio.run(run_scavenge())
                        status_box.empty()
                        
                        if isinstance(result_json, dict) and result_json.get("status") in ["error", "warning"]:
                            # Handle error/warning
                            if result_json["status"] == "error":
                                st.error(f"Search failed: {result_json.get('message')}")
                                if result_json.get("raw_content"):
                                    with st.expander("Debug Info"):
                                        st.write(result_json["raw_content"])
                            else:
                                st.warning(f"Search Warning: {result_json.get('message')}")
                                st.info("The agent returned text instead of data.")
                                with st.expander("Agent Message"):
                                    st.write(result_json.get("raw_content"))
                        
                        elif result_json:
                            # Success path - result_json is the data dict
                            st.session_state[scavenge_key] = result_json
                            st.toast(f"Scavenge complete in {turns} turns!", icon="\u2705")
                            st.rerun()
                        else:
                            st.warning("No data returned.")

                    except Exception as e:
                        st.error(f"Scavenge error: {str(e)}")

    else:
        # --- Empty Skeleton ---
        skeleton_content = textwrap.dedent("""
            <div class="obs-header" style="color:#333">NO SELECTION</div>
            <div class="obs-sub" style="color:#333">PLEASE SELECT A ROW</div>
            <br>
            <div style="color:#444;font-style:italic">Select a company to view details and scavenge for data.</div>
        """)
        st.markdown(
            f'<div class="obsidian-card">{skeleton_content}</div>',
            unsafe_allow_html=True,
        )
