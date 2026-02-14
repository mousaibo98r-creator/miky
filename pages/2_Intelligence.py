import streamlit as st

st.title("\U0001f578\ufe0f Intelligence Matrix")

# --- Heavy imports ONLY inside this page ---
import pandas as pd
import time
from services.data_loader import load_buyers

# --- Data loads AFTER title renders ---
df = load_buyers()

if df is not None and not df.empty:
    df_intel = df.copy()
else:
    # Mock fallback
    import random
    names = ["TechGlobal Inc", "Oceanic Trade", "FastLogistics", "Alpha Foods", "Zenith Parts"]
    countries = ["USA", "Germany", "China", "UK", "UAE", "Turkey"]
    mock_data = []
    for i in range(50):
        mock_data.append({
            "buyer_name": random.choice(names),
            "country_english": random.choice(countries),
            "total_usd": random.randint(1000, 100000),
            "email": [f"contact{i}@example.com"],
            "exporters": {"Mock Exporter": 1},
            "phone": [f"+1-555-01{i:02d}"],
            "address": [f"{random.randint(100,999)} Business Rd"],
            "website": ["http://example.com"]
        })
    df_intel = pd.DataFrame(mock_data)
    st.info("No data file found. Showing demo data.")

# --- Layout ---
col_filters, col_table, col_profile = st.columns([1, 3, 2])

with col_filters:
    st.markdown("### Filters")
    countries = sorted(list(df_intel['country_english'].dropna().unique()))
    sel_country = st.multiselect("Country", options=countries)
    txt_search = st.text_input("Search Buyer/Exporter")

    dff = df_intel.copy()
    if sel_country:
        dff = dff[dff['country_english'].isin(sel_country)]
    if txt_search:
        dff = dff[dff['buyer_name'].str.contains(txt_search, case=False, na=False)]
    st.info(f"Showing {len(dff)} records")

with col_table:
    st.markdown("### Data Matrix")
    if not dff.empty:
        display_cols = ['buyer_name', 'country_english', 'total_usd']
        dff = dff.copy()
        dff['emails_display'] = dff['email'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        event = st.dataframe(
            dff[display_cols + ['emails_display']],
            column_config={
                "buyer_name": "Buyer Name",
                "country_english": "Country",
                "total_usd": st.column_config.NumberColumn("Total USD", format="$%.2f"),
                "emails_display": "Emails"
            },
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
    else:
        event = None

with col_profile:
    st.markdown("### Entity Profile")
    if event and event.selection.rows:
        idx = event.selection.rows[0]
        record = dff.iloc[idx]

        st.markdown(f"<div style='font-size:1.5rem;font-weight:bold;color:#00d2ff;border-bottom:2px solid #00d2ff;padding-bottom:10px'>{record['buyer_name']}</div>", unsafe_allow_html=True)

        st.markdown(f"**\U0001f4cd Country:** {record.get('country_english', 'N/A')}")

        emails = record.get('email', [])
        st.markdown(f"**\U0001f4e7 Email:** {', '.join(emails) if isinstance(emails, list) else str(emails)}")

        phones = record.get('phone', [])
        st.markdown(f"**\U0001f4de Phone:** {', '.join(phones) if isinstance(phones, list) else str(phones)}")

        websites = record.get('website', [])
        st.markdown(f"**\U0001f310 Website:** {', '.join(websites) if isinstance(websites, list) else str(websites)}")

        st.divider()

        val = record.get('total_usd', 0)
        st.markdown(f"**\U0001f4b0 Total Volume:** ${val:,.2f}")

        st.markdown("**\U0001f6a2 Exporters:**")
        exporters = record.get('exporters', {})
        if isinstance(exporters, dict):
            for k, v in exporters.items():
                st.markdown(f"- {k} ({v} invoices)")

        st.divider()
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("\U0001f310 Google Search", f"https://www.google.com/search?q={record['buyer_name']}")
        with b2:
            if st.button("\U0001f985 Scavenge Data"):
                with st.spinner("Scavenging web..."):
                    time.sleep(1.5)
                st.success("Data scavenged!")
    else:
        st.info("Select a row in the table to view profile.")
