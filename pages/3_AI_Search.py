import streamlit as st

st.title("\U0001f916 AI Search (DeepSeek)")
st.caption("Enrich buyer contact data using DeepSeek AI with web search capabilities.")

import os

from services.data_loader import get_buyer_names, get_countries, load_buyers

# --- Data loads AFTER title ---
data = load_buyers()

# Check API key availability
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not api_key:
    st.warning("DeepSeek API key not configured. Set DEEPSEEK_API_KEY in Settings or .env file.")

# --- Buyer selection ---
st.markdown("### Select Buyer to Enrich")
col1, col2 = st.columns(2)

with col1:
    buyer_names = get_buyer_names(data)
    if buyer_names:
        selected_buyer = st.selectbox("Buyer Name", options=buyer_names)
    else:
        selected_buyer = st.text_input("Buyer Name", placeholder="Enter buyer name...")

with col2:
    country_list = get_countries(data)
    if country_list:
        selected_country = st.selectbox("Country", options=country_list)
    else:
        selected_country = st.text_input("Country", placeholder="Enter country...")

# Show current data for selected buyer
if data and selected_buyer:
    record = None
    for item in data:
        if item.get("buyer_name") == selected_buyer:
            record = item
            break
    if record:
        with st.expander("Current Data", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Emails:** {', '.join(record.get('email', [])) or 'None'}")
                st.markdown(f"**Phones:** {', '.join(record.get('phone', [])) or 'None'}")
            with c2:
                st.markdown(f"**Website:** {', '.join(record.get('website', [])) or 'None'}")
                st.markdown(f"**Address:** {', '.join(record.get('address', [])) or 'None'}")

st.divider()

# --- AI Enrichment (ONLY on button click) ---
if st.button("\U0001f680 Enrich with AI", type="primary", disabled=not api_key):
    if not selected_buyer or not selected_country:
        st.error("Please select both a buyer and a country.")
    else:
        from services.ai_client import enrich_buyer

        status_container = st.status("AI Enrichment in progress...", expanded=True)
        progress = st.progress(0)

        logs = []

        def status_callback(msg):
            logs.append(msg)
            status_container.write(msg)
            # Approximate progress based on log count
            progress.progress(min(len(logs) * 10, 90))

        # Run async function
        try:
            import asyncio

            result, turns = asyncio.run(
                enrich_buyer(selected_buyer, selected_country, status_callback)
            )
        except Exception as e:
            result = None
            turns = 0
            st.error(f"AI Search failed: {e}")

        progress.progress(100)

        if result:
            status_container.update(label="Enrichment complete!", state="complete")
            st.success(f"Found data in {turns} AI turns!")

            st.markdown("### Enriched Results")
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("**\U0001f4e7 Emails Found:**")
                for e in result.get("email", []):
                    st.markdown(f"- {e}")

                st.markdown("**\U0001f4de Phones Found:**")
                for p in result.get("phone", []):
                    st.markdown(f"- {p}")

            with col_b:
                st.markdown("**\U0001f310 Websites Found:**")
                for w in result.get("website", []):
                    st.markdown(f"- [{w}]({w})")

                st.markdown("**\U0001f4cd Addresses Found:**")
                for a in result.get("address", []):
                    st.markdown(f"- {a}")

            if result.get("notes"):
                st.info(f"Notes: {result['notes']}")
        else:
            status_container.update(label="No results found", state="error")
            st.warning(
                "AI search returned no results. The buyer may not have public contact information."
            )
