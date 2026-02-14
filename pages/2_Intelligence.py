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

# --- Layout: Filters in Sidebar, Main Area: [Table, Profile] ---
with st.sidebar:
    st.markdown("### \U0001f50d Filters")
    # Use destination_country for filtering
    country_col = "destination_country"
    if country_col not in df_intel.columns:
        country_col = "country_english"  # fallback
    countries = sorted(list(df_intel[country_col].dropna().unique()))
    sel_country = st.multiselect("Country", options=countries)
    txt_search = st.text_input("Search Buyer/Exporter")

    st.divider()

    dff = df_intel.copy()
    if sel_country:
        dff = dff[dff[country_col].isin(sel_country)]
    if txt_search:
        dff = dff[dff["buyer_name"].str.contains(txt_search, case=False, na=False)]
    st.info(f"Showing {len(dff)} records")

col_table, col_profile = st.columns([5, 2])

with col_table:
    st.markdown("### Data Matrix")
    if not dff.empty:
        display_cols = ["buyer_name", country_col, "total_usd"]
        dff = dff.copy()
        dff["emails_display"] = dff["email"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        event = st.dataframe(
            dff[display_cols + ["emails_display"]],
            column_config={
                "buyer_name": "Buyer Name",
                country_col: "Country",
                "total_usd": st.column_config.NumberColumn("Total USD", format="$%.2f"),
                "emails_display": "Emails",
            },
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )
    else:
        event = None

with col_profile:
    st.markdown("### Entity Profile")

    # --- CSS (Global for Obsidian Card) ---
    st.markdown(
        """
        <style>
            .obsidian-card {
                background-color: #111;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 24px;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                min-height: 480px; /* Ensure visual presence */
            }
            .obs-header {
                font-size: 1.6rem;
                font-weight: 700;
                color: #a38cf4; /* Light purple */
                margin-bottom: 4px;
                line-height: 1.2;
            }
            .obs-sub {
                font-size: 0.8rem;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 24px;
            }
            .obs-section-label {
                font-size: 0.7rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .obs-value {
                font-size: 1.1rem;
                font-weight: 600;
                color: #fff;
            }
            .obs-placeholder {
                color: #444;
                font-style: italic;
            }
            .obs-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
                margin-bottom: 24px;
                border-bottom: 1px solid #222;
                padding-bottom: 24px;
            }
            .obs-list-section {
                margin-bottom: 20px;
            }
            .obs-list-title {
                color: #a38cf4;
                font-size: 0.85rem;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 10px;
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

        # Location info
        dest_country = record.get("destination_country", "N/A")
        try:
            # Clean up Turkey/Azerbaijan encodings if present in UI only
            dest_country = dest_country.replace("İ", "I").replace("Ç", "C").replace("Ş", "S")
        except AttributeError:
            pass

        country_code = record.get("country_code", "")
        location_str = f"{dest_country} ({country_code})" if country_code else dest_country

        # Metrics
        volume = record.get("total_usd", 0)

        # Contact lists
        emails = record.get("email", [])
        websites = record.get("website", [])
        phones = record.get("phone", [])
        addresses = record.get("address", [])

        def render_list_items(items, color="#00ffcc"):
            if not isinstance(items, list) or not items:
                return "<div style='color:#555;font-style:italic;font-size:0.85rem'>None</div>"
            html = ""
            for it in items:
                html += f"<div style='margin-bottom:4px;color:#eee;font-size:0.9rem'><span style='color:{color};margin-right:8px'>●</span>{it}</div>"
            return html

        # --- Obsidian Style Card (Real Data) ---
        card_content = textwrap.dedent(f"""
            <!-- Header -->
            <div class="obs-header">{buyer_raw}</div>
            <div class="obs-sub">ENGLISH: {english_name}</div>

            <!-- Metrics Row -->
            <div class="obs-grid">
                <div>
                    <div class="obs-section-label">LOCATION</div>
                    <div class="obs-value">{location_str}</div>
                </div>
                <div>
                    <div class="obs-section-label">VOLUME</div>
                    <div class="obs-value">${volume:,.2f}</div>
                </div>
            </div>

            <!-- Contact Info -->
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

        st.markdown("")  # Spacer

        # --- Actions ---
        st.markdown("#### \u26a1 Actions")
        b1, b2 = st.columns([2, 1])
        with b1:
            st.link_button(
                "\U0001f30d Google Search",
                f"https://www.google.com/search?q={english_name}",
                use_container_width=True,
            )
        with b2:
            if st.button("\U0001f985 Scavenge", use_container_width=True):
                with st.spinner("Scavenging..."):
                    time.sleep(1.5)
                st.toast("Data scavenged!", icon="\u2705")

    else:
        # --- Empty Skeleton State ---
        skeleton_content = textwrap.dedent("""
            <div class="obs-header" style="color:#333">NO SELECTION</div>
            <div class="obs-sub" style="color:#333">PLEASE SELECT A ROW</div>

            <div class="obs-grid" style="border-color:#222">
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
                <div class="obs-placeholder" style="font-size:0.85rem">---</div>
            </div>

            <div class="obs-list-section">
                <div class="obs-list-title" style="color:#444">WEBSITES</div>
                <div class="obs-placeholder" style="font-size:0.85rem">---</div>
            </div>

            <div style="flex-grow:1;display:flex;align-items:center;justify-content:center;height:100px;color:#444;font-style:italic;border-top:1px solid #222;margin-top:20px">
                Select a buyer from the matrix to view intelligence profile.
            </div>
        """)
        st.markdown(
            f'<div class="obsidian-card">{skeleton_content}</div>',
            unsafe_allow_html=True,
        )
