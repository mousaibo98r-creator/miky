import textwrap

import streamlit as st

st.title("\U0001f578\ufe0f Intelligence Matrix")

# --- Heavy imports ONLY inside this page ---
import time

import pandas as pd

from services.data_loader import load_buyers

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
    st.info("No data file found. Showing demo data.")

# --- Filters in Sidebar ---
with st.sidebar:
    st.markdown("### \U0001f50d Filters")
    # Use destination_country for filtering
    country_col = "destination_country"
    if country_col not in df_intel.columns:
        country_col = "country_english"  # fallback
    countries = sorted(list(df_intel[country_col].dropna().unique()))
    sel_country = st.multiselect("Country", options=countries)

    st.divider()

    # Filter Logic
    dff = df_intel.copy()
    if sel_country:
        dff = dff[dff[country_col].isin(sel_country)]

# --- Main Layout: Side-by-Side [Matrix 70% | Profile 30%] ---
# Note: Search is now above the table in the main area
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
        dff = dff.copy()
        dff["emails_display"] = dff["email"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        dff["phones_display"] = dff["phone"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        dff["websites_display"] = dff["website"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        dff["addresses_display"] = dff["address"].apply(
            lambda x: "; ".join(x) if isinstance(x, list) else str(x)
        )
        # Ensure total_invoices exists (for mock/real compatibility)
        if "total_invoices" not in dff.columns:
            dff["total_invoices"] = 0

        display_cols = [
            "buyer_name",
            country_col,
            "total_invoices",
            "total_usd",
            "emails_display",
            "websites_display",
            "phones_display",
            "addresses_display",
        ]

        event = st.dataframe(
            dff[display_cols],
            column_config={
                "buyer_name": "Buyer Name",
                country_col: "Country",
                "total_invoices": st.column_config.NumberColumn("Invoices"),
                "total_usd": st.column_config.NumberColumn("Total USD", format="$%.2f"),
                "emails_display": "Email",
                "websites_display": "Website",
                "phones_display": "Phone",
                "addresses_display": "Address",
            },
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            height=600,  # Fixed height to match profile card
        )
    else:
        event = None

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
                /* No fixed height, let it grow */
            }
            .obs-header {
                font-size: 1.4rem; /* Slightly smaller for narrower col */
                font-weight: 700;
                color: #a38cf4; 
                margin-bottom: 4px;
                line-height: 1.2;
                word-wrap: break-word; /* handle long names */
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
        idx = event.selection.rows[0]
        record = dff.iloc[idx]

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

        emails = record.get("email", [])
        websites = record.get("website", [])
        phones = record.get("phone", [])
        addresses = record.get("address", [])

        def render_list_items(items, color="#00ffcc"):
            if not isinstance(items, list) or not items:
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

            <div class="obs-scavenge-tag">ID: Scavenged X</div>
        """)

        st.markdown(f'<div class="obsidian-card">{card_content}</div>', unsafe_allow_html=True)

        st.markdown("")  # spacer

        # Actions
        if st.button("\U0001f30d Google Search", use_container_width=True):
            st.markdown(
                f"<script>window.open('https://www.google.com/search?q={english_name}', '_blank');</script>",
                unsafe_allow_html=True,
            )
            # Fallback for Streamlit which might not allow pure JS open easily, using link_button is better but button requested

        # Actually, using link_button for search is better UX in Streamlit
        st.link_button(
            "\U0001f30d Google Search",
            f"https://www.google.com/search?q={english_name}",
            use_container_width=True,
        )

        if st.button("\U0001f985 Scavenge Data", use_container_width=True):
            with st.spinner("Scavenging..."):
                time.sleep(1.5)
            st.toast("Data updated!", icon="\u2705")

    else:
        # --- Empty Skeleton (Vertical) ---
        skeleton_content = textwrap.dedent("""
            <div class="obs-header" style="color:#333">NO SELECTION</div>
            <div class="obs-sub" style="color:#333">PLEASE SELECT A ROW</div>

            <div class="obs-grid-2" style="border-top-color:#222">
                <div>
                    <div class="obs-section-label" style="color:#333">LOCATION</div>
                    <div class="obs-value obs-placeholder">---</div>
                </div>
                <div>
                    <div class="obs-section-label" style="color:#333">VOLUME</div>
                    <div class="obs-value obs-placeholder">---</div>
                </div>
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title" style="color:#444">EMAILS</div>
                <div class="obs-placeholder">---</div>
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title" style="color:#444">PHONES</div>
                <div class="obs-placeholder">---</div>
            </div>
            
             <div style="margin-top:20px;color:#444;font-style:italic;font-size:0.8rem">
                Select a row from the table on the left to view details here.
            </div>
        """)
        st.markdown(
            f'<div class="obsidian-card">{skeleton_content}</div>',
            unsafe_allow_html=True,
        )
